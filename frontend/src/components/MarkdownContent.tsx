import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";

interface MarkdownContentProps {
  content: string;
  compact?: boolean;
}

const REMARK_PLUGINS = [remarkGfm];
const REHYPE_PLUGINS = [rehypeRaw, rehypeSanitize];
const TABLE_ROW = /^\s*\|(.+)\|\s*$/;
const TABLE_DIVIDER_CELL = /^:?-{3,}:?$/;

function cellsIn(row: string): string[] {
  const match = TABLE_ROW.exec(row);
  return match ? match[1].split("|").map((cell) => cell.trim()) : [];
}

function normalizeMarkdownTables(content: string): string {
  const lines = content.split("\n");
  const normalized: string[] = [];

  for (let index = 0; index < lines.length; ) {
    if (!TABLE_ROW.test(lines[index])) {
      normalized.push(lines[index]);
      index += 1;
      continue;
    }

    const tableRows: string[] = [];
    while (index < lines.length && TABLE_ROW.test(lines[index])) {
      tableRows.push(lines[index]);
      index += 1;
    }

    const hasDivider = tableRows.some((row) => {
      const cells = cellsIn(row);
      return cells.length > 0 && cells.every((cell) => TABLE_DIVIDER_CELL.test(cell));
    });
    if (tableRows.length > 1 && !hasDivider) {
      const columnCount = cellsIn(tableRows[0]).length;
      normalized.push(
        `| ${Array.from({ length: columnCount }, () => " ").join(" | ")} |`,
        `| ${Array.from({ length: columnCount }, () => "---").join(" | ")} |`,
      );
    }
    normalized.push(...tableRows);
  }

  return normalized.join("\n");
}

export function MarkdownContent({ content, compact = false }: MarkdownContentProps) {
  const textSize = compact ? "text-sm leading-6" : "font-serif text-[17px] leading-8";

  return (
    <div className={`min-w-0 text-slate-200 ${textSize}`}>
      <ReactMarkdown
        remarkPlugins={REMARK_PLUGINS}
        rehypePlugins={REHYPE_PLUGINS}
        components={{
          h1: ({ children }) => <h1 className="mt-7 mb-3 text-2xl font-semibold text-slate-50">{children}</h1>,
          h2: ({ children }) => <h2 className="mt-7 mb-3 text-xl font-semibold text-slate-50">{children}</h2>,
          h3: ({ children }) => <h3 className="mt-6 mb-2 text-lg font-semibold text-slate-100">{children}</h3>,
          p: ({ children }) => <p className="my-3 first:mt-0 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold text-slate-50">{children}</strong>,
          em: ({ children }) => <em className="text-slate-100">{children}</em>,
          ul: ({ children }) => <ul className="my-3 list-disc space-y-1 pl-6">{children}</ul>,
          ol: ({ children }) => <ol className="my-3 list-decimal space-y-1 pl-6">{children}</ol>,
          li: ({ children }) => <li className="pl-1">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="my-4 border-l-2 border-amber-200/50 pl-4 text-slate-300">{children}</blockquote>
          ),
          a: ({ children, href }) => (
            <a href={href} target="_blank" rel="noreferrer" className="text-amber-200 underline decoration-amber-200/30 underline-offset-4 hover:text-amber-100">
              {children}
            </a>
          ),
          code: ({ children }) => <code className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[0.88em] text-amber-100">{children}</code>,
          table: ({ children }) => (
            <div className="my-5 max-w-full overflow-x-auto rounded-xl border border-slate-700">
              <table className="w-full min-w-lg border-collapse text-left font-sans text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-slate-800/90 text-slate-100">{children}</thead>,
          tbody: ({ children }) => <tbody className="divide-y divide-slate-800">{children}</tbody>,
          tr: ({ children }) => <tr className="align-top even:bg-slate-900/45">{children}</tr>,
          th: ({ children }) => <th className="border-r border-slate-700 px-3 py-2.5 text-xs font-semibold last:border-r-0">{children}</th>,
          td: ({ children }) => <td className="border-r border-slate-800 px-3 py-2.5 text-slate-300 last:border-r-0">{children}</td>,
        }}
      >
        {normalizeMarkdownTables(content)}
      </ReactMarkdown>
    </div>
  );
}
