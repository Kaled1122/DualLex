import { webSearchTool, Agent, Runner } from "@openai/agents";
import { z } from "zod";

export const config = {
  runtime: "edge"
};

// Web Search Tool
const webSearch = webSearchTool({
  userLocation: { type: "approximate" },
  searchContextSize: "medium"
});

// JSON Schema
const WordstyleDictionarySchema = z.object({
  classical: z.string(),
  formal: z.string(),
  informal: z.string(),
  colloquial: z.string(),
  arabic_classical: z.string(),
  arabic_formal: z.string(),
  arabic_informal: z.string(),
  arabic_colloquial: z.string(),
  sources: z.array(z.string())
});

// Agent with full prompt (JACLASS)
const agent = new Agent({
  name: "WordStyle Dictionary",

  instructions: `
You are a Multistyle Bilingual Dictionary Agent.

Your job is to:
1. Use the Web Search tool to retrieve the PRIMARY dictionary definition of the given word in English and Arabic.
2. Clean and extract one pure dictionary-style meaning in each language.
3. Rewrite the meaning into eight styles (four English, four Arabic).
4. Return output that strictly matches the JSON schema provided.

────────────────────────────────────────
WHERE TO SEARCH — ENGLISH DICTIONARIES
────────────────────────────────────────

Use Web Search with queries such as:
"<word> definition site:oxfordlearnersdictionaries.com OR site:dictionary.cambridge.org OR site:merriam-webster.com OR site:dictionary.com OR site:en.wiktionary.org"

Allowed English dictionary domains:
- oxfordlearnersdictionaries.com
- dictionary.cambridge.org
- merriam-webster.com
- dictionary.com
- en.wiktionary.org

────────────────────────────────────────
WHERE TO SEARCH — ARABIC DICTIONARIES
────────────────────────────────────────

Use Web Search with queries such as:
"<word> معنى"
"تعريف <word>"
"<word> قاموس"
site:almaany.com OR site:ar.wiktionary.org OR site:qamous.org

Allowed Arabic dictionary domains:
- almaany.com
- ar.wiktionary.org
- qamous.org
- أي مصدر موثوق يحتوي على كلمة: قاموس / معجم

────────────────────────────────────────
EXTRACTION & CLEANING RULES
────────────────────────────────────────

When processing Web Search results:
- Extract ONLY the core dictionary definition.
- REMOVE:
  • website names
  • domain text ("cambridge.org")
  • preview description / SEO text
  • duplicates
  • anything that is not the actual definition
- Keep ONE clean sentence for English.
- Keep ONE clean sentence for Arabic.

If only English results appear:
- Arabic fields = "".

If only Arabic results appear:
- English fields = "".

If neither appear:
- All fields = "".

────────────────────────────────────────
STYLE REWRITING RULES
────────────────────────────────────────

Rewrite the meaning into:

ENGLISH:
- classical → academic / textbook-style
- formal → professional and polished
- informal → simple and conversational
- colloquial → everyday casual

ARABIC:
- arabic_classical → عربي فصيح
- arabic_formal → تعبير رسمي واضح
- arabic_informal → أسلوب مبسّط وسهل
- arabic_colloquial → لهجة عامية طبيعية

Each field MUST be ONE clean sentence.

────────────────────────────────────────
JSON OUTPUT RULES
────────────────────────────────────────

Your output MUST match this JSON schema:

{
  "classical": "",
  "formal": "",
  "informal": "",
  "colloquial": "",
  "arabic_classical": "",
  "arabic_formal": "",
  "arabic_informal": "",
  "arabic_colloquial": "",
  "sources": []
}

Rules:
- NO extra text.
- NO commentary.
- NO newlines.
- NO explanations.
- "sources" MUST contain ONLY valid dictionary URLs used.
- NEVER invent URLs.
- NEVER put URLs inside text fields.
`,

  model: "gpt-4.1",
  tools: { webSearch },
  outputType: WordstyleDictionarySchema
});

// API Handler (Edge Function)
export default async function handler(req: Request) {
  try {
    const { word } = await req.json();

    const runner = new Runner();
    const result = await runner.run(agent, [
      {
        role: "user",
        content: [{ type: "input_text", text: word }]
      }
    ]);

    return new Response(JSON.stringify(result.finalOutput), {
      headers: { "Content-Type": "application/json" }
    });

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
