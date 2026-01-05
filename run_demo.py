"""Run a tiny demo: classification + ReAct simple flow.
"""
import os
from src.vision.vision_service import classify_image
from src.agent.react_agent import run_react




def demo():
    # simple image classify demo (user provides path)
    img = input("Image path (or press enter to skip): ")
    if img:
        labels = classify_image(img)
        print("Vision results:", labels)
        # ask agent to combine
        q = f"我上傳了一張圖片，模型辨識結果 {labels}。請幫我總結並建議下一步。"
        ans = run_react(q)
        print("Agent final answer:\n", ans)
    else:
        q = input("Enter a question for the agent (e.g. 'Strawberry 有幾個 r？'):\n")
        ans = run_react(q)
        print(ans)


if __name__ == '__main__':
    demo()