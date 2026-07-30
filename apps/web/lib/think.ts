export interface SplitContent {
  thinking: string;
  answer: string;
  isThinking: boolean;
}

export function splitThinking(content: string): SplitContent {
  const openIndex = content.indexOf("<think>");
  if (openIndex === -1) {
    return { thinking: "", answer: content, isThinking: false };
  }

  const afterOpen = content.slice(openIndex + "<think>".length);
  const closeIndex = afterOpen.indexOf("</think>");
  const before = content.slice(0, openIndex);

  if (closeIndex === -1) {
    return { thinking: afterOpen, answer: before, isThinking: true };
  }

  const thinking = afterOpen.slice(0, closeIndex);
  const after = afterOpen.slice(closeIndex + "</think>".length);
  return { thinking, answer: before + after, isThinking: false };
}
