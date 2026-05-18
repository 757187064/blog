import fs from "node:fs";
import type { Dirent } from "node:fs";
import path from "node:path";

export interface RepositoryItem {
  name: string;
  path: string;
  href: string;
  type: "file" | "directory";
  size?: string;
}

export interface RepositoryMeta {
  slug: string;
  title: string;
  category: string;
  description: string;
  root: string;
}

export const repositories: RepositoryMeta[] = [
  {
    slug: "deeplearning",
    title: "Deep Learning",
    category: "课程笔记",
    description: "深度学习课程资料、阅读材料、课件、作业和 notebook。",
    root: "deeplearning"
  }
];

const publicRoot = path.join(process.cwd(), "public", "project-storage");
const ignoredNames = new Set([
  ".DS_Store",
  ".git",
  ".idea",
  ".ipynb_checkpoints",
  "__pycache__",
  "node_modules"
]);

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(1)} GB`;
}

function encodePath(value: string) {
  return value.split("/").map(encodeURIComponent).join("/");
}

export function getRepository(slug: string) {
  return repositories.find((repository) => repository.slug === slug);
}

export function getRepositoryItems(repository: RepositoryMeta, subPath = "") {
  const absolutePath = path.join(publicRoot, repository.root, subPath);
  if (!absolutePath.startsWith(path.join(publicRoot, repository.root))) return [];
  if (!fs.existsSync(absolutePath)) return [];

  const entries: Dirent[] = fs
    .readdirSync(absolutePath, { withFileTypes: true })
    .filter((entry: Dirent) => !ignoredNames.has(entry.name) && !entry.name.startsWith("."));

  return entries
    .map((entry: Dirent): RepositoryItem => {
      const itemPath = path.join(subPath, entry.name).replaceAll(path.sep, "/");
      const itemAbsolutePath = path.join(absolutePath, entry.name);
      const stat = fs.statSync(itemAbsolutePath);
      const type = entry.isDirectory() ? "directory" : "file";

      return {
        name: entry.name,
        path: itemPath,
        href:
          type === "directory"
            ? `/files/${repository.slug}/${encodePath(itemPath)}/`
            : `/project-storage/${repository.root}/${encodePath(itemPath)}`,
        type,
        size: type === "file" ? formatSize(stat.size) : undefined
      };
    })
    .sort((a: RepositoryItem, b: RepositoryItem) => {
      if (a.type !== b.type) return a.type === "directory" ? -1 : 1;
      return a.name.localeCompare(b.name, "zh-CN");
    });
}

export function countRepositoryFiles(repository: RepositoryMeta) {
  const root = path.join(publicRoot, repository.root);
  let files = 0;
  let directories = 0;

  function walk(current: string) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (ignoredNames.has(entry.name) || entry.name.startsWith(".")) continue;
      const next = path.join(current, entry.name);
      if (entry.isDirectory()) {
        directories += 1;
        walk(next);
      } else {
        files += 1;
      }
    }
  }

  if (fs.existsSync(root)) walk(root);
  return { files, directories };
}
