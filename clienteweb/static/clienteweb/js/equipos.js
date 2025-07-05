const equipoModal = document.getElementById('equipoSearchModal');
    const modalSearchInput = document.getElementById('modalSearchInput');
    const modalResultsList = document.getElementById('modalResultsList');
    const mainEquipoInput = document.getElementById('equipo');
    const paginationControls = document.getElementById('modalPaginationControls');

    let allEquipos = [];
    let filteredEquipos = [];
    let currentPage = 1;
    const itemsPerPage = 20;

    if (equipoModal) {
        // ... El código de los eventos 'show.bs.modal' e 'input' no cambia ...
        equipoModal.addEventListener('show.bs.modal', async function() {
            if (allEquipos.length === 0) {
                modalResultsList.innerHTML = '<p class="text-center">Cargando equipos...</p>';
                try {
                    const response = await fetch('/api/equipos/');
                    if (!response.ok) throw new Error('No se pudieron cargar los equipos.');
                    allEquipos = await response.json();
                    filteredEquipos = [...allEquipos];
                    goToPage(1);
                } catch (error) {
                    modalResultsList.innerHTML = `<p class="text-danger text-center">${error.message}</p>`;
                }
            }
        });
        modalSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            filteredEquipos = allEquipos.filter(equipo => {
                const code = String(equipo.Code || '').toLowerCase();
                const name = String(equipo.Name || '').toLowerCase();
                return code.includes(searchTerm) || name.includes(searchTerm);
            });
            goToPage(1);
        });
    }

    // ... La función goToPage no cambia ...
    function goToPage(pageNumber) {
        currentPage = pageNumber;
        renderEquiposList();
        renderPaginationControls();
    }

    // ... La función renderEquiposList no cambia ...
    function renderEquiposList() {
        modalResultsList.innerHTML = '';
        if (filteredEquipos.length === 0) {
            modalResultsList.innerHTML = '<p class="text-center">No se encontraron equipos que coincidan.</p>';
            return;
        }
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pageItems = filteredEquipos.slice(startIndex, endIndex);
        const list = document.createElement('ul');
        list.className = 'list-group';
        pageItems.forEach(equipo => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item list-group-item-action';
            listItem.style.cursor = 'pointer';
            listItem.dataset.code = equipo.Code;
            listItem.textContent = `${equipo.Code} - ${equipo.Name}`;
            listItem.addEventListener('click', function() {
                // 1. Obtenemos el código del equipo desde el atributo 'data-code' de la fila
                const equipoCode = this.dataset.code;

                // 2. Verificamos que obtuvimos un código
                if (equipoCode) {
                 // 3. Construimos la nueva URL a la que vamos a redirigir
                 const currentUrl = window.location.pathname; // Esto es '/equipos/'
                 const newUrl = `${currentUrl}?id=${equipoCode}`;
        
                console.log(`Redirigiendo a: ${newUrl}`);
        
                 // 4. Le decimos al navegador que vaya a esa nueva URL.
                 // ¡Y listo! El trabajo del JavaScript termina aquí.
                 window.location.href = newUrl;
                   }
            });
            list.appendChild(listItem);
        });
        modalResultsList.appendChild(list);
    }


    // =================================================================
    //         FUNCIÓN DE PAGINACIÓN ACTUALIZADA Y MEJORADA
    // =================================================================
    /**
     * Dibuja los botones de control de la paginación de forma inteligente.
     */
    function renderPaginationControls() {
        paginationControls.innerHTML = '';
        const totalPages = Math.ceil(filteredEquipos.length / itemsPerPage);

        if (totalPages <= 1) return;

        const ul = document.createElement('ul');
        ul.className = 'pagination';

        // Función auxiliar para crear un item de paginación
        const createPageItem = (page, text = page, disabled = false, active = false) => {
            const li = document.createElement('li');
            li.className = `page-item ${disabled ? 'disabled' : ''} ${active ? 'active' : ''}`;
            const a = document.createElement('a');
            a.className = 'page-link';
            a.href = '#';
            a.innerHTML = text;
            a.addEventListener('click', (e) => {
                e.preventDefault();
                if (!disabled) goToPage(page);
            });
            li.appendChild(a);
            return li;
        };
        
        // Botón "Anterior"
        ul.appendChild(createPageItem(currentPage - 1, '&laquo;', currentPage === 1));

        // Lógica para mostrar números y elipsis
        const pageRange = 2; // Cuántas páginas mostrar alrededor de la actual
        let lastPageRendered = 0;

        for (let i = 1; i <= totalPages; i++) {
            if (
                i === 1 || // Siempre mostrar la primera página
                i === totalPages || // Siempre mostrar la última página
                (i >= currentPage - pageRange && i <= currentPage + pageRange) // Mostrar páginas en el rango cercano
            ) {
                if (lastPageRendered && i - lastPageRendered > 1) {
                    // Si hay un salto, añadir elipsis
                    ul.appendChild(createPageItem(0, '...', true));
                }
                ul.appendChild(createPageItem(i, i, false, i === currentPage));
                lastPageRendered = i;
            }
        }

        // Botón "Siguiente"
        ul.appendChild(createPageItem(currentPage + 1, '&raquo;', currentPage === totalPages));

        paginationControls.appendChild(ul);
    }
