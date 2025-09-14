import json

import dspy
from pydantic import BaseModel

from enum import Enum
from datetime import datetime
from typing import List, Optional, Literal

class Essay(BaseModel):
    PostTitle: str
    Content: str
    Keywords: List[str]
    Author: str
    Date: datetime

class EssaySignature(dspy.Signature):
    """
    Convert the email essay and into proper markdown (full essay) and extract metadata
    Add Author and date just after the post title in markdown.
    """
    text: str = dspy.InputField()
    essay: Essay = dspy.OutputField()

class TitleSignature(dspy.Signature):
    """
    Given the essay generate an appropriate blog entry title
    """
    essay: Essay = dspy.InputField()
    entry_title : str = dspy.OutputField()

class EssayConverter(dspy.Module):
    def __init__(self):
        self.essay_gen = dspy.Predict(EssaySignature)
        self.title_gen = dspy.Predict(TitleSignature)

    def __call__(self, text: str) -> str:
        essay_pred = self.essay_gen(text=text)
        title_pred = self.title_gen(essay=essay_pred)
        essay = essay_pred.essay
        essay.PostTitle = title_pred.entry_title
        return essay

def convert(text: str) -> Essay:
    # module = dspy.Predict(EssaySignature)
    module = EssayConverter()

    lm = dspy.LM("gemini/gemini-2.5-flash", temperature=1.0, max_tokens=64000, cache=False)

    with dspy.context(lm=lm):
        essay = module(text=text)

    return essay


if __name__ == "__main__":
    import sys

    # Check if input is from stdin or file argument
    if len(sys.argv) == 2:
        # Read from file
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    elif len(sys.argv) == 1:
        # Read from stdin
        text = sys.stdin.read()
    else:
        print("Usage: python convert.py [text_file]")
        print("Or pipe input: cat file.txt | python convert.py")
        sys.exit(1)

    # Convert the text
    essay = convert(text)

    # Print the converted markdown
    print(essay.Content)
    print(essay.PostTitle)
