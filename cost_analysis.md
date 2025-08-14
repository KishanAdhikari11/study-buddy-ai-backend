# 🧠 LLM Cost Comparison for AI Quiz & Flashcard Generator (2025 Edition)

This README presents a **comprehensive cost analysis** for using modern Large Language Models (LLMs) to build an AI-powered **quiz and flashcard generation app**. It compares leading commercial APIs (OpenAI, Google, Anthropic, Cohere, Microsoft, Alibaba, xAI), hosted open-source models (Fireworks, Together, Replicate), and **self-hosted** solutions (LLaMA, Mistral, Mixtral).

---

## ✅ Use Case

- **Task**: Generate quizzes & flashcards from ~1,000-word input (≈3,000 tokens total).
- **Goal**: Find the most **cost-effective**, **scalable**, and **high-performing** LLM solution.

---

## 📊 Proprietary LLM API Pricing (Per ~3,000 Tokens)

| **Provider / Model**             | **Prompt ($/1K)** | **Completion ($/1K)** | **Est. Cost / Doc** |
|----------------------------------|-------------------|------------------------|----------------------|
| OpenAI GPT-4 Turbo               | $0.0020           | $0.0080                | ~$0.0300             |
| OpenAI GPT-3.5 Turbo             | $0.0015           | $0.0020                | ~$0.0105             |
| Google Gemini 1.5 Pro            | $0.00125          | $0.0050                | ~$0.0188             |
| **Google Gemini 1.5 Flash**      | **$0.000075**     | **$0.000300**          | **~$0.0011**         |
| Anthropic Claude 3 Sonnet        | $0.0030           | $0.0150                | ~$0.0540             |
| Anthropic Claude 3 Haiku         | $0.0008           | $0.0040                | ~$0.0045             |
| Cohere Command R+                | $0.0025           | $0.0100                | ~$0.0375             |
| Cohere Command R                 | $0.00015          | $0.00060               | ~$0.0023             |
| **Microsoft Phi-4-mini (Azure)** | **$0.000075**     | **$0.000300**          | **~$0.0006**         |
| **Alibaba Qwen-Turbo**           | **$0.00005**      | **$0.00020**           | **~$0.0004**         |
| **xAI Grok-3-mini**              | **$0.30**         | **$0.50**              | **~$0.0012**         |
| AWS Bedrock: LLaMA 2 Chat 13B    | $0.00075          | $0.00100               | ~$0.0026             |
| AWS Bedrock: LLaMA 2 Chat 70B    | $0.00195          | $0.00256               | ~$0.0068             |

---

## 🏆 Best Proprietary API-Based Options

- 🟢 **Alibaba Qwen-Turbo** – ~$0.0004/document
- 🟢 **Microsoft Phi-4-mini** – ~$0.0006/document
- 🟢 **Google Gemini Flash** – ~$0.0011/document
- 🟢 **Cohere Command R** – ~$0.0023/document

---

## 🌐 Hosted Open-Source LLMs

| **Provider**     | **Model**               | **Pricing (Input/Output)**       | **Est. Cost / Doc** |
|------------------|-------------------------|----------------------------------|----------------------|
| Replicate        | Claude 3.7 Sonnet       | $3.00 / $15.00 per million       | ~$0.0540             |
| Together AI      | LLaMA 4 Scout           | $0.18 / $0.59 per million        | ~$0.0023             |
| Together AI      | Mistral 7B              | ~$0.20 per 1K tokens             | ~$0.0060             |
| Fireworks AI     | Base <4B                | ~$0.10 per million               | ~$0.0003             |
| Fireworks AI     | LLaMA 4 Maverick        | $0.22 / $0.88 per million        | ~$0.0033             |
| Fireworks AI     | **Mixtral 8×7B (MoE)**  | ~$0.50 per million               | **~$0.0015**         |

---

## 💻 Self-Hosting Cost Estimates

| **Model**         | **GPU Needed**         | **GPU Hourly** | **Tokens/sec** | **Cost per 1M tokens** | **Est. Doc Cost** |
|-------------------|------------------------|----------------|----------------|------------------------|-------------------|
| LLaMA 7B          | A10/T4 (10 GB+)        | ~$0.60–$1.50   | ~5M/hr         | ~$0.075                | ~$0.0002          |
| Mistral 7B        | A100 (16 GB+)          | ~$1.50         | ~5.5M/hr       | ~$0.075                | ~$0.0002          |
| LLaMA 13B         | 24 GB+ GPU             | ~$2–$3         | ~3M/hr         | ~$0.10                 | ~$0.0003          |
| Mixtral 8×7B      | 56 GB+ multi-GPU       | ~$3–$6         | ~1.5M/hr       | ~$0.30                 | ~$0.0009          |
| LLaMA 70B         | 80–96 GB (H100)        | ~$3–$12        | ~600K–1.5M/hr  | ~$0.68+                | ~$0.0020+         |

> ⚠️ Self-hosting reduces per-token cost drastically **at scale**, but requires DevOps expertise and GPUs.

---

## 🆓 Free Tiers & Trials

| **Provider**      | **Free Tier / Trial Info**                                  |
|-------------------|-------------------------------------------------------------|
| OpenAI            | No free tier; initial $5–$18 credits for new users          |
| Google Gemini     | Free tier via AI Studio (low rate limits)                   |
| Cohere            | Trial key available (rate-limited)                          |
| Claude/Anthropic  | No free tier (credit-based access only)                     |
| Fireworks, Together, Replicate | Free credits ($1–$5) with rate limits          |

---

## 🎯 Recommendation Table

| **Use Case**                    | **Recommended Model**             | **Cost / Doc**     |
|----------------------------------|----------------------------------|--------------------|
| Prototyping / Hobby Projects     | Qwen-Turbo, Phi-4-mini           | ~$0.0004–0.0006    |
| Scaling Mid-size Projects        | Gemini Flash, Cohere R           | ~$0.001–0.0023     |
| Fully Open / Cheap Hosted        | Fireworks <4B, Mixtral 8×7B      | ~$0.0003–0.0015    |
| Enterprise / High-Volume         | Self-hosted Mistral or LLaMA     | ~$0.0002–0.0010    |

---

## 📚 Sources

- OpenAI: https://openai.com/pricing  
- Google Gemini: https://ai.google.dev/pricing  
- Claude: https://docs.anthropic.com/  
- Cohere: https://cohere.com/pricing  
- Microsoft Phi: https://techcommunity.microsoft.com  
- Qwen: https://qwenlm.github.io  
- Grok (xAI): https://x.ai  
- Together AI: https://together.ai  
- Fireworks AI: https://fireworks.ai  
- Replicate: https://replicate.com  
- AWS Bedrock: https://aws.amazon.com/bedrock/pricing  
- GPU Rates: https://paperspace.com | https://tensordock.com  

---

## 👨‍💻 Author

Created by **[Your Name]** – tired of being surprised by LLM token bills.  
Open to feedback, contributions, or startup funding 😉

---

## 📎 License

MIT License — feel free to use, fork, and adapt.
