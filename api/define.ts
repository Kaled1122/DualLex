import { webSearchTool, Agent, Runner, withTrace } from "@openai/agents";
import { z } from "zod";

export const config = {
  runtime: "edge"
};

// Web search tool
const webSearch = webSearchTool({
  userLocation: { type: "approximate" },
  searchContextSize: "medium"
});

// Output schema
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

// Agent definition
const wordstyleDictionary = new Agent({
  name: "WordStyle Dictionary",
  instructions: `Your entire prompt goes here EXACTLY`,
  model: "gpt-4.1",
  tools: {
    webSearch
  },
  outputType: WordstyleDictionarySchema,
  modelSettings: {
    temperature: 0.3,
    topP: 0.58,
    maxTokens: 3000
  }
});

// API endpoint
export default async (req: Request) => {
  try {
    const { word } = await req.json();

    const runner = new Runner();
    const result = await withTrace("dictionary", async () => {
      return await runner.run(wordstyleDictionary, [
        { role: "user", content: [{ type: "input_text", text: word }] }
      ]);
    });

    return new Response(JSON.stringify(result.finalOutput), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });

  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
};
