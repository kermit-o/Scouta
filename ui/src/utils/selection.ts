export function getSelectedProjectId(): string | null {
  try {
    const v = localStorage.getItem('lastProjectId');
    return v && v !== 'null' && v !== 'undefined' ? v : null;
  } catch { return null; }
}
