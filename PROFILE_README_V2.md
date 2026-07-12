![Sai Mohan Raja Reddy — AI Engineer](./header.png)

<p align="center">
  <a href="https://portfolio-six-mu-13.vercel.app"><img src="https://img.shields.io/badge/Portfolio-0D1117?style=for-the-badge&logo=vercel&logoColor=white" /></a>
  <a href="https://www.linkedin.com/in/sai-mohan-raja-reddy-janna-reddy-4309291a4/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
  <a href="mailto:saimohanrajareddyjannareddy@gmail.com"><img src="https://img.shields.io/badge/Email-0D1117?style=for-the-badge&logo=gmail&logoColor=EA4335" /></a>
</p>

---

## I build LLM systems that run unattended

The model call is the easy part. The hard part is everything around it — validation, retries, recovery, and knowing when the system is confidently wrong.

Most of my work is in **restaurant technology**: document extraction pipelines processing real invoices for real operators, and a multi-tenant RAG assistant serving 1,000+ users. Both taught the same lesson — *an agent that's right 95% of the time is worthless without a way to catch the other 5%.*

**Now:** AI Engineer @ MetaxurX · MS Computer Science, University of Central Missouri
**Building:** agent runtime internals — evaluation harnesses, memory write policies, sandboxed tool execution

---

## Things I've shipped that people actually use

### 🧾 [Ai-Invoice](https://github.com/saimohanrajareddyjannareddy/Ai-Invoice) — invoice extraction, fully autonomous

Scrapes supplier invoices daily, extracts every line item with a vision model, validates, and lands normalized records in a spend ledger. **Running in production for restaurant operators.**

The interesting part isn't the extraction — it's the validation layer that quarantines bad data before it reaches the ledger. Every failure path either quarantines or no-ops. Nothing corrupt gets in silently, nothing is dropped without a trace.

`99%+ line-item accuracy` · `zero corrupted rows since validation shipped` · `~$1.50/month to run`

<sub>GPT-4 Vision · Playwright · Supabase · n8n · Node.js</sub>

### 💬 Turmeric RAG Assistant — multi-tenant retrieval, 1,000+ users

Conversational assistant for restaurants. Vector retrieval with fallback routing when the index returns nothing useful, and tenant-aware isolation so one restaurant's data never leaks into another's context.

`1,000+ users` · `92% satisfaction` · `multi-tenant by design`

<sub>OpenAI · Pinecone · RAG · webhook orchestration</sub>

### 🍽️ [SmartMealPlanner](https://github.com/saimohanrajareddyjannareddy/SmartMealPlanner)

Recommendation API with auth and persistent user state, deployed on AWS.

<sub>Flask · MongoDB · AWS EC2</sub>

---

## Stack

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
</p>
<p>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Anthropic-191919?style=flat-square&logo=anthropic&logoColor=white" />
  <img src="https://img.shields.io/badge/Pinecone-000000?style=flat-square&logo=pinecone&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white" />
</p>
<p>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white" />
  <img src="https://img.shields.io/badge/Supabase-3FCF8E?style=flat-square&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white" />
</p>

---

## What I'm thinking about

**Verification is the bottleneck.** Generation is nearly solved; knowing whether the generation is *correct* is not. Most production LLM failures I've hit weren't bad outputs — they were bad outputs nobody caught.

**Deterministic beats clever.** Every place I could replace a model call with a rule, the system got more reliable and cheaper. The model should reason. Code should execute.

**Multi-tenancy is a safety problem, not a scaling problem.** Isolation failures in retrieval are silent, and they're the ones that end contracts.

---

<div align="center">

<img height="140" src="https://github-readme-stats.vercel.app/api?username=saimohanrajareddyjannareddy&show_icons=true&hide=stars,issues&hide_border=true&hide_title=true&bg_color=0D1117&text_color=8B949E&icon_color=58A6FF&title_color=E6EDF3" />
<img height="140" src="https://github-readme-streak-stats.herokuapp.com/?user=saimohanrajareddyjannareddy&hide_border=true&background=0D1117&stroke=30363D&ring=58A6FF&fire=58A6FF&currStreakLabel=E6EDF3&sideLabels=8B949E&dates=6E7681" />

</div>

---

<p align="center">
  <sub>Open to AI/ML engineering roles · Authorized to work in the US · St. Louis, MO</sub>
</p>
