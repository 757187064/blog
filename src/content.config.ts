import { defineCollection, z } from "astro:content";

const blog = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    draft: z.boolean().default(false),
    section: z.enum(["i write", "i prefer"]).default("i write"),
    tags: z.array(z.string()).default([]),
    hero: z.string().optional(),
    externalUrl: z.string().url().optional()
  })
});

export const collections = { blog };
