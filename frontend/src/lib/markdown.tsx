import React from "react";

export function renderInline(text: string, key: number): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return (
    <React.Fragment key={key}>
      {parts.map((part, i) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={i}>{part.slice(2, -2)}</strong>
        ) : (
          <React.Fragment key={i}>{part}</React.Fragment>
        )
      )}
    </React.Fragment>
  );
}

/**
 * Tiny renderer for the constrained markdown subset produced by the
 * backend SynthesisAgent: ##/### headings, "- " bullet lists, **bold**,
 * "> " blockquotes, and plain paragraphs.
 */
export function SimpleMarkdown({ text }: { text: string }): React.ReactElement {
  const lines = text.split("\n");
  const blocks: React.ReactNode[] = [];
  let listBuffer: string[] = [];
  let key = 0;

  const flushList = () => {
    if (listBuffer.length) {
      blocks.push(
        <ul key={`ul-${key++}`}>
          {listBuffer.map((item, i) => (
            <li key={i}>{renderInline(item, i)}</li>
          ))}
        </ul>
      );
      listBuffer = [];
    }
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (line === "") {
      flushList();
      continue;
    }
    if (line.startsWith("## ")) {
      flushList();
      blocks.push(<h2 key={key++}>{renderInline(line.slice(3), key)}</h2>);
    } else if (line.startsWith("### ")) {
      flushList();
      blocks.push(<h3 key={key++}>{renderInline(line.slice(4), key)}</h3>);
    } else if (line.startsWith("- ")) {
      listBuffer.push(line.slice(2));
    } else if (line.startsWith("> ")) {
      flushList();
      blocks.push(<blockquote key={key++}>{renderInline(line.slice(2), key)}</blockquote>);
    } else {
      flushList();
      blocks.push(<p key={key++}>{renderInline(line, key)}</p>);
    }
  }
  flushList();

  return <div className="orca-markdown">{blocks}</div>;
}
