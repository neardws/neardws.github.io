import fs from "node:fs/promises";
import path from "node:path";
import { log } from "./logger.js";

export type MemoryEntry = {
  id: string;
  content: string;
  category: MemoryCategory;
  timestamp: string;
  source: string;
  metadata?: Record<string, unknown>;
};

export type ProfileResult = {
  static: string[];   // Persistent facts about user
  dynamic: string[];  // Recent context
};

export const MEMORY_CATEGORIES = [
  "preference",
  "fact", 
  "decision",
  "entity",
  "context",
  "other",
] as const;

export type MemoryCategory = (typeof MEMORY_CATEGORIES)[number];

export function detectCategory(text: string): MemoryCategory {
  const lower = text.toLowerCase();
  if (/prefer|like|love|hate|want|favorite/i.test(lower)) return "preference";
  if (/decided|will use|going with|chose/i.test(lower)) return "decision";
  if (/\+\d{10,}|@[\w.-]+\.\w+|is called|named/i.test(lower)) return "entity";
  if (/recently|today|yesterday|just now|earlier/i.test(lower)) return "context";
  if (/is|are|has|have|works|lives/i.test(lower)) return "fact";
  return "other";
}
