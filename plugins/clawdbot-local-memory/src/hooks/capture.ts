import type { LocalMemoryClient } from "../client.js";
import type { LocalMemoryConfig } from "../config.js";
import { log } from "../logger.js";

function getLastTurn(messages: unknown[]): unknown[] {
  let lastUserIdx = -1;
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg && typeof msg === "object" && 
        (msg as Record<string, unknown>).role === "user") {
      lastUserIdx = i;
      break;
    }
  }
  return lastUserIdx >= 0 ? messages.slice(lastUserIdx) : messages;
}

function extractTextContent(msg: unknown): string {
  if (!msg || typeof msg !== "object") return "";
  const msgObj = msg as Record<string, unknown>;
  const content = msgObj.content;

  if (typeof content === "string") return content;
  
  if (Array.isArray(content)) {
    const parts: string[] = [];
    for (const block of content) {
      if (block && typeof block === "object") {
        const b = block as Record<string, unknown>;
        if (b.type === "text" && typeof b.text === "string") {
          parts.push(b.text);
        }
      }
    }
    return parts.join("\n");
  }
  
  return "";
}

// Simple fact extraction without LLM (rule-based)
function extractFacts(userText: string, assistantText: string): string[] {
  const facts: string[] = [];
  const combined = `${userText}\n${assistantText}`.toLowerCase();
  
  // Extract preferences
  const prefPatterns = [
    /i (?:really )?(?:like|love|prefer|enjoy|hate|dislike) ([^.!?]+)/gi,
    /my favorite (?:is|are) ([^.!?]+)/gi,
  ];
  
  for (const pattern of prefPatterns) {
    const matches = userText.matchAll(pattern);
    for (const m of matches) {
      if (m[1] && m[1].length > 3 && m[1].length < 100) {
        facts.push(m[0].trim());
      }
    }
  }
  
  // Extract facts about user
  const factPatterns = [
    /i (?:am|work as|live in|study|have) ([^.!?]+)/gi,
    /my (?:name|job|work|home|city) is ([^.!?]+)/gi,
  ];
  
  for (const pattern of factPatterns) {
    const matches = userText.matchAll(pattern);
    for (const m of matches) {
      if (m[1] && m[1].length > 3 && m[1].length < 100) {
        facts.push(m[0].trim());
      }
    }
  }
  
  return facts.slice(0, 5); // Limit to 5 facts per turn
}

export function buildCaptureHandler(
  client: LocalMemoryClient,
  cfg: LocalMemoryConfig
) {
  return async (event: Record<string, unknown>) => {
    if (!event.success || !Array.isArray(event.messages) || event.messages.length === 0) {
      return;
    }

    const lastTurn = getLastTurn(event.messages);
    
    let userText = "";
    let assistantText = "";
    
    for (const msg of lastTurn) {
      if (!msg || typeof msg !== "object") continue;
      const msgObj = msg as Record<string, unknown>;
      const role = msgObj.role;
      const text = extractTextContent(msg);
      
      if (role === "user") userText += text + "\n";
      if (role === "assistant") assistantText += text + "\n";
    }

    // Skip if too short
    if (userText.length < 20 && assistantText.length < 20) return;

    // Skip system-injected context (avoid capturing our own recall output)
    if (userText.includes("<local-memory-context>") || 
        userText.includes("local-memory-context") ||
        userText.includes("Relevant Memories")) {
      log.debug("skipping capture: detected system-injected memory context");
      return;
    }

    // Extract facts using rule-based approach
    const facts = extractFacts(userText, assistantText);
    
    if (facts.length > 0) {
      log.debug(`extracted ${facts.length} facts from conversation`);
      
      for (const fact of facts) {
        await client.addMemory(fact, undefined, "auto-capture");
      }
    }

    // Also store the conversation summary if substantial
    if (userText.length > 50) {
      const summary = userText.slice(0, 200).trim();
      await client.addMemory(
        `User discussed: ${summary}`,
        "context",
        "auto-capture"
      );
    }
  };
}
