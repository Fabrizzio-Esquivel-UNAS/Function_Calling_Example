document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://127.0.0.1:8000';
    const contactForm = document.getElementById('contact-form');
    const contactList = document.getElementById('contact-list');
    const contactIdField = document.getElementById('contact-id');
    const searchForm = document.getElementById('search-form');
    const searchIdField = document.getElementById('search-id');
    const resetSearchBtn = document.getElementById('reset-search');
    const clearFormBtn = document.getElementById('clear-form');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatBox = document.getElementById('chat-box');
    const chatSubmitBtn = document.getElementById('chat-submit-btn');

    // --- Funciones del CRUD ---

    const displayContacts = (contacts) => {
        contactList.innerHTML = '';
        contacts.forEach(contact => {
            const contactItem = document.createElement('div');
            contactItem.className = 'contact-item';
            contactItem.innerHTML = `
                <span>${contact.nombre} - ${contact.telefono}</span>
                <div>
                    <button class="edit-btn" data-id="${contact.id}">Editar</button>
                    <button class="delete-btn" data-id="${contact.id}">Eliminar</button>
                </div>
            `;
            contactList.appendChild(contactItem);
        });
    };

    const fetchContacts = async () => {
        try {
            const response = await fetch(`${apiUrl}/contactos`);
            const contacts = await response.json();
            displayContacts(contacts);
        } catch (error) {
            console.error('Error al cargar contactos:', error);
        }
    };

    const searchContact = async (e) => {
        e.preventDefault();
        const id = searchIdField.value;
        if (!id) {
            fetchContacts();
            return;
        }
        try {
            const response = await fetch(`${apiUrl}/contactos/${id}`);
            if (response.ok) {
                const contact = await response.json();
                displayContacts([contact]);
            } else {
                contactList.innerHTML = '<p>Contacto no encontrado.</p>';
            }
        } catch (error) {
            console.error('Error al buscar contacto:', error);
            contactList.innerHTML = '<p>Error al buscar el contacto.</p>';
        }
    };

    const clearForm = () => {
        contactForm.reset();
        contactIdField.value = '';
    };

    const saveContact = async (e) => {
        e.preventDefault();
        const id = contactIdField.value;
        const contactData = {
            nombre: document.getElementById('nombre').value,
            telefono: document.getElementById('telefono').value,
            email: document.getElementById('email').value,
            direccion: document.getElementById('direccion').value,
            ciudad: document.getElementById('ciudad').value,
            pais: document.getElementById('pais').value,
            fecha_nacimiento: document.getElementById('fecha_nacimiento').value,
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${apiUrl}/contactos/${id}` : `${apiUrl}/contactos`;

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(contactData),
            });
            if (response.ok) {
                clearForm();
                fetchContacts();
            } else {
                console.error('Error al guardar el contacto');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const editContact = async (id) => {
        try {
            const response = await fetch(`${apiUrl}/contactos/${id}`);
            const contact = await response.json();
            contactIdField.value = contact.id;
            document.getElementById('nombre').value = contact.nombre;
            document.getElementById('telefono').value = contact.telefono;
            document.getElementById('email').value = contact.email || '';
            document.getElementById('direccion').value = contact.direccion || '';
            document.getElementById('ciudad').value = contact.ciudad || '';
            document.getElementById('pais').value = contact.pais || '';
            document.getElementById('fecha_nacimiento').value = contact.fecha_nacimiento || '';
        } catch (error) {
            console.error('Error al cargar contacto para editar:', error);
        }
    };

    const deleteContact = async (id) => {
        if (confirm('¿Estás seguro de que quieres eliminar este contacto?')) {
            try {
                const response = await fetch(`${apiUrl}/contactos/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    fetchContacts();
                } else {
                    console.error('Error al eliminar el contacto');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    };

    contactList.addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-btn')) {
            editContact(e.target.dataset.id);
        }
        if (e.target.classList.contains('delete-btn')) {
            deleteContact(e.target.dataset.id);
        }
    });

    // --- Funciones del Chat ---

    const addMessageToChatBox = (message, sender) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', `${sender}-message`);
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        addMessageToChatBox(prompt, 'user');
        chatInput.value = '';
        chatSubmitBtn.disabled = true;

        try {
            const response = await fetch(`${apiUrl}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt }),
            });
            const data = await response.json();
            const assistantMessage = data.content || JSON.stringify(data);
            addMessageToChatBox(assistantMessage, 'assistant');
        } catch (error) {
            console.error('Error en el chat:', error);
            addMessageToChatBox('Error al conectar con el asistente.', 'assistant');
        } finally {
            chatSubmitBtn.disabled = false;
        }
    };

    // --- Inicialización ---
    contactForm.addEventListener('submit', saveContact);
    searchForm.addEventListener('submit', searchContact);
    resetSearchBtn.addEventListener('click', fetchContacts);
    clearFormBtn.addEventListener('click', clearForm);
    chatForm.addEventListener('submit', handleChatSubmit);
    fetchContacts();
});
