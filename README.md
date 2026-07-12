![Sai Mohan Raja Reddy — AI Engineer<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="320" viewBox="0 0 1280 320">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0D1117"/>
      <stop offset="60%" stop-color="#0F1620"/>
      <stop offset="100%" stop-color="#131C2B"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2F81F7"/>
      <stop offset="100%" stop-color="#1F6FEB" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#2F81F7" stroke-opacity="0.07" stroke-width="1"/>
    </pattern>
    <radialGradient id="glow" cx="0.78" cy="0.5" r="0.55">
      <stop offset="0%" stop-color="#2F81F7" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#2F81F7" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="1280" height="320" fill="url(#bg)"/>
  <rect width="1280" height="320" fill="url(#grid)"/>
  <rect width="1280" height="320" fill="url(#glow)"/>

  <!-- node graph motif, right side: agent loop -->
  <g stroke="#2F81F7" stroke-opacity="0.5" fill="none" stroke-width="1.5">
    <path d="M960 120 L1060 96 M1060 96 L1150 140 M1150 140 L1090 216 M1090 216 L985 205 M985 205 L960 120 M1060 96 L1090 216 M960 120 L1150 140"/>
  </g>
  <g fill="#0D1117" stroke="#58A6FF" stroke-width="2">
    <circle cx="960" cy="120" r="7"/>
    <circle cx="1060" cy="96" r="7"/>
    <circle cx="1150" cy="140" r="7"/>
    <circle cx="1090" cy="216" r="7"/>
    <circle cx="985" cy="205" r="7"/>
  </g>
  <circle cx="1060" cy="96" r="13" fill="none" stroke="#58A6FF" stroke-opacity="0.35" stroke-width="1.5"/>
  <circle cx="1090" cy="216" r="13" fill="none" stroke="#58A6FF" stroke-opacity="0.35" stroke-width="1.5"/>

  <!-- accent rule -->
  <rect x="88" y="108" width="220" height="3" fill="url(#accent)" rx="1.5"/>

  <text x="88" y="176" font-family="'Helvetica Neue',Helvetica,Arial,sans-serif" font-size="52" font-weight="600" fill="#E6EDF3" letter-spacing="-0.5">Sai Mohan Raja Reddy</text>

  <text x="88" y="218" font-family="'SF Mono',Menlo,Consolas,monospace" font-size="20" fill="#58A6FF" letter-spacing="0.5">AI Engineer</text>
  <text x="228" y="218" font-family="'SF Mono',Menlo,Consolas,monospace" font-size="20" fill="#484F58">·</text>
  <text x="248" y="218" font-family="'SF Mono',Menlo,Consolas,monospace" font-size="20" fill="#8B949E" letter-spacing="0.5">Agentic Systems &#183; RAG Pipelines</text>

  <text x="88" y="256" font-family="'Helvetica Neue',Helvetica,Arial,sans-serif" font-size="16" fill="#6E7681">Building agent runtimes that fail safely.</text>
</svg>
]()
<img width="1280" height="320" alt="header" src="https://github.com/user-attachments/assets/094fa80f-f94c-4de9-a48a-a459d1b9a9ab" />

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
