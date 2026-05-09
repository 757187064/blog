declare const process: {
  cwd(): string;
};

declare module "node:fs" {
  export interface Dirent {
    name: string;
    isDirectory(): boolean;
  }

  export interface Stats {
    size: number;
  }

  interface ReaddirOptions {
    withFileTypes: true;
  }

  export function readdirSync(path: string, options: ReaddirOptions): Dirent[];
  export function statSync(path: string): Stats;
  export function existsSync(path: string): boolean;

  const fs: {
    readdirSync: typeof readdirSync;
    statSync: typeof statSync;
    existsSync: typeof existsSync;
  };

  export default fs;
}

declare module "node:path" {
  export const sep: string;
  export function join(...paths: string[]): string;

  const path: {
    sep: typeof sep;
    join: typeof join;
  };

  export default path;
}
