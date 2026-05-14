export function getGreetingContext() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Bom dia';
  if (hour < 18) return 'Boa tarde';
  return 'Boa noite';
}

export function formatFirstName(user) {
  if (!user) return '';
  const name = user.first_name || user.name;
  if (!name || name.includes('@')) return '';
  return name.split(' ')[0];
}
