/** Ubah label rujukan [chunk-n] jadi link markdown ke anchor panel rujukan (#citation-n). */
export function linkifyCitations(text: string): string {
  return text.replace(/\[chunk-(\d+)\]/g, (_match, n) => `[${n}](#citation-${n})`);
}
