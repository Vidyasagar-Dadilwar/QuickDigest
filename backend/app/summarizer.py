from transformers import pipeline
import os
import math
from typing import List
from dotenv import load_dotenv

load_dotenv()

HF_MODEL = os.getenv("HF_MODEL", "sshleifer/distilbart-cnn-12-6")

# instantiate once
summarizer = pipeline("summarization", model=HF_MODEL, device=-1)  # device=-1 => CPU

# map minutes to configuration
TIME_MAP = {
    5: {"articles": 5, "max_tokens": 40},      # 1-liners
    10: {"articles": 8, "max_tokens": 80},     # short
    20: {"articles": 12, "max_tokens": 140},   # medium
    30: {"articles": 20, "max_tokens": 220},   # detailed
    60: {"articles": 30, "max_tokens": 320},   # in-depth
}

def chunk_text(text: str, max_words=400):
    words = text.split()
    n = math.ceil(len(words) / max_words)
    chunks = []
    for i in range(n):
        chunk = " ".join(words[i*max_words:(i+1)*max_words])
        chunks.append(chunk)
    return chunks

def summarize_article(text: str, max_tokens: int):
    """
    If article is very long, chunk it, summarize each chunk, then combine.
    """
    chunks = chunk_text(text, max_words=500)  # ~500 words per chunk
    summaries = []
    for c in chunks:
        try:
            out = summarizer(c, max_length=max_tokens, min_length=max(10, int(max_tokens/3)), do_sample=False)[0]['summary_text']
        except Exception as e:
            # fallback: short extractive fallback (first 2 paragraphs)
            out = " ".join(c.split("\n\n")[:2])
        summaries.append(out)
    if len(summaries) == 1:
        return summaries[0]
    # combine chunk summaries and compress into final summary
    combined = " ".join(summaries)
    try:
        final = summarizer(combined, max_length=max_tokens, min_length=max(20, int(max_tokens/2)), do_sample=False)[0]['summary_text']
        return final
    except Exception:
        return combined