import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Componente a probar
import EmptyState from './EmptyState';

describe('EmptyState', () => {
  test('renders the provided message', () => {
    // Renderiza el componente con un mensaje
    render(<EmptyState message="No players found" />);
    // Verifica que el texto aparezca en el DOM
    expect(screen.getByText('No players found')).toBeInTheDocument();
  });

  test('renders with different message', () => {
    // Debe funcionar con cualquier mensaje
    render(<EmptyState message="No data available" />);
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });

  test('applies correct CSS class', () => {
    // Acceso al contenedor para verificar clases CSS
    const { container } = render(<EmptyState message="Test" />);
    const emptyDiv = container.querySelector('.empty-message');

    expect(emptyDiv).toBeInTheDocument();
    // Asegura que el contenido se muestra en la clase esperada
    expect(emptyDiv).toHaveTextContent('Test');
  });

  test('renders empty string message', () => {
    // Debe permitir cadena vacía como mensaje válido
    render(<EmptyState message="" />);
    const emptyDiv = screen.getByText('', { selector: '.empty-message' });
    expect(emptyDiv).toBeInTheDocument();
  });
});
