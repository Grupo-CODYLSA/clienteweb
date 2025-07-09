document.addEventListener('DOMContentLoaded', function () {
    
    // ===================================================================
    //  SELECTORES DE ELEMENTOS
    // ===================================================================
    // Para la lógica de filtros
    const btnAplicarFiltros = document.getElementById('btnAdaptarFiltros');
    const filtroEstadoSelect = document.getElementById('Estado');

    // Para la lógica de checkboxes y contador
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const rowCheckboxes = document.querySelectorAll('.row-checkbox');
    const aprobacionCountSpan = document.getElementById('aprobacionCount');

    // Para la lógica de colapso de filas
    const collapsibleRows = document.querySelectorAll('.collapse');


    // ===================================================================
    //  LÓGICA DE FILTROS (RECARGA LA PÁGINA)
    // ===================================================================
    if (btnAplicarFiltros && filtroEstadoSelect) {
        btnAplicarFiltros.addEventListener('click', function (event) {
            event.preventDefault(); // Evitamos que el formulario se envíe

            const estadoSeleccionado = filtroEstadoSelect.value;
            
            // Construimos la nueva URL con el parámetro de estado
            // Ej: /proceso-aprobacion/?estado=Aprobado
            const nuevaUrl = `${window.location.pathname}?estado=${estadoSeleccionado}`;
            
            // Redirigimos a la nueva URL para que Django filtre los datos
            window.location.href = nuevaUrl;
        });
    }


    // ===================================================================
    //  LÓGICA DE CHECKBOXES Y CONTADOR (TU CÓDIGO ORIGINAL)
    // ===================================================================

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
        if (aprobacionCountSpan) {
            aprobacionCountSpan.textContent = `(${selectedRows} / ${totalRows})`;
        }

        // Controlar el estado del checkbox principal (seleccionar todo)
        if (selectAllCheckbox) {
            if (totalRows === 0) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            } else if (selectedRows === totalRows) {
                selectAllCheckbox.checked = true;
                selectAllCheckbox.indeterminate = false;
            } else if (selectedRows > 0) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = true;
            } else {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            }
        }
    }

    // 1. Lógica para el checkbox principal (seleccionar/deseleccionar todo)
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateAprobacionCount(); // Actualizar el conteo
        });
    }

    // 2. Lógica para los checkboxes de cada fila
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateAprobacionCount(); // Actualizar el conteo
        });
    });

    // Inicializar el conteo cuando la página carga
    updateAprobacionCount();


    // ===================================================================
    //  LÓGICA PARA COLAPSO DE FILAS (TU CÓDIGO ORIGINAL)
    // ===================================================================
    collapsibleRows.forEach(row => {
        // Evento ANTES de que la fila se muestre
        row.addEventListener('show.bs.collapse', function () {
            const triggerButton = document.querySelector(`[data-bs-target="#${row.id}"]`);
            if (triggerButton) {
                const icon = triggerButton.querySelector('i');
                icon.classList.remove('bi-chevron-down');
                icon.classList.add('bi-chevron-up');
            }
        });

        // Evento ANTES de que la fila se oculte
        row.addEventListener('hide.bs.collapse', function () {
            const triggerButton = document.querySelector(`[data-bs-target="#${row.id}"]`);
            if (triggerButton) {
                const icon = triggerButton.querySelector('i');
                icon.classList.remove('bi-chevron-up');
                icon.classList.add('bi-chevron-down');
            }
        });
    });

});