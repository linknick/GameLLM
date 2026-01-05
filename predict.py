import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import xgboost as xgb
class BPpredictor:
    PICK_WEIGHTS = np.array([1/1,1/2,1/3,1/4,1/5])  # 可調
    def __init__(self, games_df, hero_df,modelName = None):
        if modelName!= None: 
            self.model = xgb.Booster()
            self.model.load_model(modelName)
        # parse columns
        for col in ['team1_picks','team2_picks','team1_bans','team2_bans','winner','patch','league']:
            if col not in games_df.columns:
                games_df[col] = np.nan
        games_df['team1_picks'] = games_df['team1_picks'].apply(self.parse_list_field)
        games_df['team2_picks'] = games_df['team2_picks'].apply(self.parse_list_field)
        games_df['team1_bans']  = games_df['team1_bans'].apply(self.parse_list_field)
        games_df['team2_bans']  = games_df['team2_bans'].apply(self.parse_list_field)
        
        
        # normalize winner field to 1 if team1 won else 0
        def normalize_winner(w):
            if pd.isna(w):
                return np.nan
            w = str(w).lower()
            if w in ['team1','1','true','t','yes','win','won','blue']:
                return 1
            else:
                return 0
        games_df['label_team1_win'] = games_df['winner'].apply(normalize_winner)

        # drop rows without proper picks or labels
        games_df = games_df[games_df['team1_picks'].apply(len) >= 1]
        games_df = games_df[games_df['team2_picks'].apply(len) >= 1]
        games_df = games_df[~games_df['label_team1_win'].isna()].reset_index(drop=True)

        
        self.all_heroes = set()
        for _, r in games_df.iterrows():
            self.all_heroes.update(r['team1_picks'])
            self.all_heroes.update(r['team2_picks'])
            self.all_heroes.update(r['team1_bans'])
            self.all_heroes.update(r['team2_bans'])
        
        self.all_heroes = sorted([h for h in self.all_heroes if h and h.lower() != 'nan'])
        
        self.hero_to_idx = {h: i for i, h in enumerate(self.all_heroes)}
        self.idx_to_hero = {i: h for h, i in self.hero_to_idx.items()}
        self.num_heroes = len(self.hero_to_idx)
        print(self.all_heroes)
        print("英雄數量:", self.num_heroes)
        
        """
        hero_df = hero_df[hero_df['is_pick']==1][['role','champion']]
        self.hero_to_pos = {h: p for p, h in enumerate(self.all_heroes)}
        self.pos_to_hero = {p: h for h, p in self.hero_to_idx.items()}
        """
        
        
        
        counts_vs = np.zeros((self.num_heroes, self.num_heroes), dtype=np.int32)
        
        wins_vs   = np.zeros((self.num_heroes, self.num_heroes), dtype=np.int32)
        counts_sy = np.zeros((self.num_heroes, self.num_heroes), dtype=np.int32)
        wins_sy   = np.zeros((self.num_heroes, self.num_heroes), dtype=np.int32)

        for _, r in games_df.iterrows():
            t1 = [self.hero_to_idx[h] for h in r['team1_picks'] if h in self.hero_to_idx]
            t2 = [self.hero_to_idx[h] for h in r['team2_picks'] if h in self.hero_to_idx]
            t1_win = int(r['label_team1_win'])
            # counters: each pair (a in t1, b in t2)
            for a in t1:
                for b in t2:
                    counts_vs[a, b] += 1
                    wins_vs[a, b] += t1_win
                    counts_vs[b, a] += 1
                    wins_vs[b, a] += (1 - t1_win)  # from other perspective
            # synergy: pairs within same team
            for i in range(len(t1)):
                for j in range(i+1, len(t1)):
                    a, b = t1[i], t1[j]
                    counts_sy[a,b] += 1
                    wins_sy[a,b] += t1_win
                    counts_sy[b,a] += 1
                    wins_sy[b,a] += t1_win
            for i in range(len(t2)):
                for j in range(i+1, len(t2)):
                    a, b = t2[i], t2[j]
                    counts_sy[a,b] += 1
                    wins_sy[a,b] += (1 - t1_win)
                    counts_sy[b,a] += 1
                    wins_sy[b,a] += (1 - t1_win)

        # Laplace smoothing to get probabilities
        self.alpha = 1.0
        self.counter_prob = (wins_vs + self.alpha) / (counts_vs + 2*self.alpha)  # shape (n,n)
        self.synergy_prob = (wins_sy + self.alpha) / (counts_sy + 2*self.alpha)
        
    def parse_list_field(self,x):
        # 支援多種格式：list, "a,b,c" , "['a','b']"
        if isinstance(x, list):
            return [i for i in x if i is not None and str(i) != 'nan']
        s = str(x).strip()
        if s.startswith('[') and (',' in s):
            s2 = s.strip("[]")
            parts = [p.strip().strip("'\"") for p in s2.split(',') if p.strip()]
            return parts
        if ',' in s:
            return [p.strip() for p in s.split(',') if p.strip()]
        if s == '':
            return []
        return [s]
    def encode(self, data):
        
        def weighted_pick_vector(picks):
            v = np.zeros(self.num_heroes, dtype=np.float32)
            for i, h in enumerate(picks):
                if h in self.hero_to_idx:
                    w = self.PICK_WEIGHTS[i] if i < len(self.PICK_WEIGHTS) else self.PICK_WEIGHTS[-1]
                    v[self.hero_to_idx[h]] += w
            return v

        def compute_counter_feature(team_picks_idx, opp_picks_idx):
            # average pairwise counter probability: mean of counter_prob[a,b] for all a in team, b in opp
            if len(team_picks_idx) == 0 or len(opp_picks_idx) == 0:
                return 0.0
            s = 0.0
            cnt = 0
            for a in team_picks_idx:
                for b in opp_picks_idx:
                    s += self.counter_prob[a,b]
                    cnt += 1
            return s / cnt

        def compute_synergy_feature(team_picks_idx):
            if len(team_picks_idx) < 2:
                return 0.0
            s = 0.0
            cnt = 0
            for i in range(len(team_picks_idx)):
                for j in range(i+1, len(team_picks_idx)):
                    a = team_picks_idx[i]; b = team_picks_idx[j]
                    s += self.synergy_prob[a,b]
                    cnt += 1
            return (s / cnt) if cnt>0 else 0.0
        t1_picks = [self.hero_to_idx[h] for h in data['team1_picks'] if h in self.hero_to_idx]
        t2_picks = [self.hero_to_idx[h] for h in data['team2_picks'] if h in self.hero_to_idx]
        t1_bans  = [self.hero_to_idx[h] for h in data['team1_bans']  if h in self.hero_to_idx]
        t2_bans  = [self.hero_to_idx[h] for h in data['team2_bans']  if h in self.hero_to_idx]
        # one-hot vectors
        t1_pick_oh = np.zeros(self.num_heroes, dtype=np.float32)
        t2_pick_oh = np.zeros(self.num_heroes, dtype=np.float32)
        t1_ban_oh  = np.zeros(self.num_heroes, dtype=np.float32)
        t2_ban_oh  = np.zeros(self.num_heroes, dtype=np.float32)
        for a in t1_picks: t1_pick_oh[a] = 1.0
        for a in t2_picks: t2_pick_oh[a] = 1.0
        for a in t1_bans:  t1_ban_oh[a]  = 1.0
        for a in t2_bans:  t2_ban_oh[a]  = 1.0
        
        # weighted pick vectors (preserve order)
        t1_pick_w = weighted_pick_vector(data['team1_picks'])
        t2_pick_w = weighted_pick_vector(data['team2_picks'])
        
        # counter features
        t1_vs_t2_counter = compute_counter_feature(t1_picks, t2_picks)
        t2_vs_t1_counter = compute_counter_feature(t2_picks, t1_picks)
        # synergy features
        t1_synergy = compute_synergy_feature(t1_picks)
        t2_synergy = compute_synergy_feature(t2_picks)

        # assemble feature vector (concat)
        feat = np.concatenate([
            t1_pick_oh, t1_ban_oh, t1_pick_w,
            t2_pick_oh, t2_ban_oh, t2_pick_w,
            np.array([t1_vs_t2_counter, t2_vs_t1_counter, t1_synergy, t2_synergy], dtype=np.float32)
        ]).astype(np.float32)
        return feat
    def onehot_from_list(lst):
        v = np.zeros(self.num_heroes, dtype=np.float32)
        for h in lst:
            if h in self.hero_to_idx:
                v[self.hero_to_idx[h]] = 1.0
        return v

    
    def train(self,data):
        
        X_list = []
        y_list = []
        meta_list = []

        for _, r in games_df.iterrows():
            
            feat = self.encode(r)
            X_list.append(feat)
            y_list.append(r['label_team1_win'])
            
            meta_list.append({"game_id": r.get("game_id")})
        
        
        X = np.stack(X_list)
        y = np.array(y_list, dtype=np.int32)
        
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        dtrain = xgb.DMatrix(X_train, label=y_train)
        
        dtest  = xgb.DMatrix(X_test, label=y_test)
        
        params = {
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "eta": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "seed": 42,
            "nthread": 4
        }
        self.model.train(params, dtrain, num_boost_round=300, evals=[(dtrain, 'train'), (dtest, 'test')], verbose_eval=50)

        y_pred_prob = self.model.predict(dtest)
        y_pred = (y_pred_prob > 0.5).astype(int)

        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_prob)
        print(f"改良版 Baseline - Accuracy: {acc:.4f}, AUC: {auc:.4f}")
        self.model.save_model("bp_predictor.model")
        
    def recommend_pick(self, data, team="blue", top_k=5):
        current_roles = np.zeros(self.num_heroes)
        for col in data:
            data[col] = self.parse_list_field(data[col])
            for hero in data[col]:
                current_roles[self.hero_to_idx[hero]] = 1
        
        
        candidates = []
        for hid in range(self.num_heroes):
            
            if current_roles[hid] != 0:  # 已經被選/ban
                continue
            hero = self.idx_to_hero[hid]
            if team =='blue':
                data['team1_picks'].append(hero)
                winrate = self.predict_winrate(data)
                candidates.append((hero, winrate))
                data['team1_picks'].pop(-1)
            else:
                
                data['team2_picks'].append(hero)
                winrate = self.predict_winrate(data)
                candidates.append((hero, 1-winrate))
                data['team2_picks'].pop(-1)

        candidates.sort(key=lambda x: x[1], reverse= True)
        
        return candidates[:top_k]

    def recommend_ban(self,data, target_team="red", top_k=5):
        current_roles = np.zeros(self.num_heroes)
        for col in data:
            data[col] = self.parse_list_field(data[col])
            for hero in data[col]:
                current_roles[self.hero_to_idx[hero]] = 1
        
        
        candidates = []
        for hid in range(self.num_heroes):
            if current_roles[hid] != 0:  # 已經被選/ban
                continue
            hero = self.idx_to_hero[hid]

            # 模擬 ban
            prev = current_roles[hid]
            if target_team == 'blue' :
                data['team1_picks'].append(hero)
                winrate = self.predict_winrate(data)
                candidates.append((hero, 1-winrate))
                data['team1_picks'].pop(-1)
            else:
                data['team2_picks'].append(hero)
                winrate = self.predict_winrate(data)
                candidates.append((hero, winrate))
                data['team2_picks'].pop(-1)
        candidates.sort(key=lambda x: x[1], reverse= True)
        return candidates[:top_k]

    def predict_winrate(self,data):
        for x in data:
            data[x]=self.parse_list_field(data[x])
        encode_vec = self.encode(data)
        dmatrix = xgb.DMatrix(encode_vec.reshape(1, -1))
        pred = self.model.predict(dmatrix)
        return float(pred[0])  # Team1 勝率

if __name__ == '__main__':
    games_df = pd.read_csv("games.csv")
    hero_df = pd.read_csv("heroes.csv")
    model = BPpredictor(games_df,hero_df,modelName="bp_predictor.model")
    #model.train(games_df)

    # 載入已訓練好的模型()
    # 假設有 N 個英雄
    N_HEROES =   model.num_heroes
    data = {"team1_picks":[],"team2_picks":[],"team1_bans":[],"team2_bans":[]}
    #可以一口氣輸入好
    data2 = {
        "team1_picks":['Neeko','Trundle','ABCDE','Sion' , 'Zeri'],
        "team2_picks":['Xin Zhao','Taliyah','Rakan','Sivir','Aatrox'],
        "team1_bans":['Pantheon','Vi','Alistar','Xayah','Gwan'],
        "team2_bans":['Azir','Wukong','Ryze','Kai\'Sa','Jhin']
    }
    
    print(model.predict_winrate(data2))
    exit()
    """
    next_pick = model.recommend_pick(data,team = 'blue',top_k = 10)
    data['team1_picks'].append(next_pick[0][0])
    print("勝率:", model.predict_winrate(data))
    data['team1_picks'].pop(-1)
    next_pick = model.recommend_pick(data,team = 'red',top_k = 10)
    print(next_pick)
    data['team2_picks'].append(next_pick[0][0])
    print("勝率:", model.predict_winrate(data))
    data['team2_picks'].pop(-1)
    print("勝率:", model.predict_winrate(data))
    """
    #也可以輪流輸入
    
    hero = model.recommend_ban(data,target_team = 'red',top_k = 10)
    print(hero)
    hero = model.recommend_ban(data,target_team = 'blue',top_k = 10)
    print(hero)
    hero = model.recommend_pick(data,team = 'blue',top_k = 10)
    print(hero)
    hero = model.recommend_pick(data,team = 'red',top_k = 10)
    print(hero)
    a,b,c,d = 0,0,0,0
    for i in range(20):
        if i in [0,2,4,13,15]:
            
            hero = model.recommend_ban(data,target_team = 'red',top_k = 10)
            print(hero)
            data["team1_bans"].append(hero[0][0])
            a+=1
        elif i in [1,3,5,12,14]:
            hero = model.recommend_ban(data,target_team = 'blue',top_k = 10)[0][0]
            data["team2_bans"].append(hero)
            b+=1
        elif i in [6,9,10,17,18]:
            hero = model.recommend_pick(data,team = 'blue',top_k = 10)[0][0]
            data["team1_picks"].append(hero)
            c+=1
        else:
            hero = model.recommend_pick(data,team = 'red',top_k = 10)[0][0]
            data["team2_picks"].append(hero)
            d+=1
        print(data)
        print("勝率:", model.predict_winrate(data))
        