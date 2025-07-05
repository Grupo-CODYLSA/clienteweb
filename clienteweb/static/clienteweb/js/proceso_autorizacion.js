// proceso_autorizacion.js

document.addEventListener('DOMContentLoaded', function () {
    // --- Lógica para el manejo de los íconos de colapso/expansión ---
    // Seleccionamos todas las filas que pueden colapsarse
    const collapsibleRows = document.querySelectorAll('.collapse');

    collapsibleRows.forEach(row => {
        // Escuchamos el evento que se dispara JUSTO ANTES de que la fila se muestre
        row.addEventListener('show.bs.collapse', function () {
            // Buscamos el botón que controla esta fila
            const triggerButton = document.querySelector(`[data-bs-target="#${row.id}"]`);
            if (triggerButton) {
                const icon = triggerButton.querySelector('i');
                // Cambiamos el ícono a "chevron-up"
                icon.classList.remove('bi-chevron-down');
                icon.classList.add('bi-chevron-up');
            }
        });

        // Escuchamos el evento que se dispara JUSTO ANTES de que la fila se oculte
        row.addEventListener('hide.bs.collapse', function () {
            // Buscamos el botón que controla esta fila
            const triggerButton = document.querySelector(`[data-bs-target="#${row.id}"]`);
            if (triggerButton) {
                const icon = triggerButton.querySelector('i');
                // Volvemos a cambiar el ícono a "chevron-down"
                icon.classList.remove('bi-chevron-up');
                icon.classList.add('bi-chevron-down');
            }
        });
    });

    // --- Lógica para el checkbox principal y el contador de aprobación ---
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const rowCheckboxes = document.querySelectorAll('.row-checkbox');
    const aprobacionCountSpan = document.getElementById('aprobacionCount');

    // Función para actualizar el contador de "Decisiones de aprobación"
    function updateAprobacionCount() {
        const totalRows = rowCheckboxes.length;
        let selectedRows = 0;

        rowCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selectedRows++;
            }
        });

        // Actualizamos el texto en el span
        aprobacionCountSpan.textContent = `(${selectedRows} / ${totalRows})`;

        // Controlar el estado del checkbox principal (seleccionar todo)
        if (totalRows === 0) { // Si no hay filas, el checkbox principal no debería estar marcado
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedRows === totalRows) { // Todas seleccionadas
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedRows > 0) { // Algunas seleccionadas
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else { // Ninguna seleccionada
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }

    // 1. Lógica para el checkbox principal (seleccionar/deseleccionar todo)
    if (selectAllCheckbox) { // Asegurarse de que el elemento exista
        selectAllCheckbox.addEventListener('change', function() {
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateAprobacionCount(); // Actualizar el conteo después de cambiar todos
        });
    }

    // 2. Lógica para los checkboxes de cada fila (actualizar el contador y el checkbox principal)
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateAprobacionCount(); // Actualizar el conteo al cambiar un checkbox individual
        });
    });

    // Inicializar el conteo cuando la página carga
    // Esto es importante para que el contador y el checkbox principal reflejen el estado inicial
    // si hay filas ya marcadas al cargar la página.
    updateAprobacionCount();
});