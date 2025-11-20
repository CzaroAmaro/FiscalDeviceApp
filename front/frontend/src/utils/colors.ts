export const statusColor = (status: string) => {
  switch (status) {
    case 'open':
      return 'blue';
    case 'in_progress':
      return 'orange';
    case 'closed':
      return 'success';
    default:
      return 'grey';
  }
};

export const resolutionColor = (resolution: string) => {
  switch (resolution) {
    case 'completed': return 'success';
    case 'failed': return 'error';
    case 'cancelled': return 'grey';
    default: return 'default';
  }
};
