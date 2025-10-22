import { mount } from '@vue/test-utils';
import { describe, expect,it } from 'vitest';
import { VChip } from 'vuetify/components'; // Importujemy konkretny komponent, którego szukamy

import DeviceStatusChip from '../DeviceStatusChip.vue';

// Nie potrzebujemy pełnej instancji Vuetify, jeśli testujemy tylko props
// Jeśli jednak inne komponenty jej wymagają, zostaw `setup.ts` bez zmian.

describe('DeviceStatusChip.vue', () => {
  it('renders correct text and passes "green" color prop for "active" status', () => {
    // Arrange
    const wrapper = mount(DeviceStatusChip, {
      props: {
        status: 'active',
      },
      // global: { plugins: [vuetify] } // Można zostawić, jeśli jest w setup.ts
    });

    // Act
    // Znajdź komponent VChip, a nie element HTML z klasą .v-chip
    const chipComponent = wrapper.findComponent(VChip);

    // Assert
    // 1. Sprawdź, czy tekst jest poprawny. To jest ważne.
    expect(chipComponent.text()).toContain('Aktywne');

    // 2. Sprawdź, czy do komponentu VChip został przekazany poprawny prop `color`.
    // To jest "kontrakt" - nasz komponent ma za zadanie przekazać "green".
    // To, co VChip z tym zrobi, to już jego sprawa, a nie nasza.
    expect(chipComponent.props('color')).toBe('green');
  });

  it('renders correct text and passes "blue" color prop for "serviced" status', () => {
    // Arrange
    const wrapper = mount(DeviceStatusChip, {
      props: {
        status: 'serviced',
      },
    });

    // Act
    const chipComponent = wrapper.findComponent(VChip);

    // Assert
    expect(chipComponent.text()).toContain('W serwisie');
    expect(chipComponent.props('color')).toBe('blue');
  });

  it('renders correct text and passes "grey" color prop for unknown status', () => {
    // Arrange
    const wrapper = mount(DeviceStatusChip, {
      props: {
        status: 'jakis_nieznany_status',
      },
    });

    // Act
    const chipComponent = wrapper.findComponent(VChip);

    // Assert
    expect(chipComponent.text()).toContain('Nieznany');
    expect(chipComponent.props('color')).toBe('grey');
  });
});
