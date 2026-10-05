// 본문이 HTML이면 그대로, 평문이면 문단(<p>)으로 변환
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
export function toHtml(text = '') {
  if (/<[a-z][\s\S]*>/i.test(text)) return text.replace(/src="assets\//g, 'src="/assets/');
  return text.split(/\n\s*\n/).filter((p) => p.trim()).map((p) => `<p>${esc(p.trim()).replace(/\n/g, '<br>')}</p>`).join('');
}
export const plain = (s = '') => s.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
export const src = (p) => (p ? '/' + p.replace(/^\//, '') : '');
