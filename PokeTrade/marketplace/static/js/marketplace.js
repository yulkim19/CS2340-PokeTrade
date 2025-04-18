document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.pokemon-card').forEach(card => {
    const dialog = card.querySelector('.pokemon-dialog'); // Dialog element
    const closeBtn = dialog.querySelector('.close-btn');  // Close button inside the dialog

    card.addEventListener('click', () => {
      dialog.showModal();  // Open the dialog
      console.log('Dialog opened');
    });

    closeBtn.addEventListener('click', () => {
      dialog.close();  // Close the dialog
      console.log('Dialog closed via close button');
    });

    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) {
        dialog.close();
        console.log('Dialog closed via backdrop');
      }
    });

    dialog.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && dialog.open) {
        dialog.close();  // Close the dialog
        console.log('Dialog closed via Escape key');
      }
    });
  });
});