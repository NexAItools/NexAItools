document.addEventListener('DOMContentLoaded', loadTasks);

const taskForm = document.getElementById('task-form');
const taskInput = document.getElementById('task-input');
const taskList = document.getElementById('task-list');

taskForm.addEventListener('submit', function(event) {
    event.preventDefault();
    addTask(taskInput.value);
    taskInput.value = '';
});

taskList.addEventListener('click', function(event) {
    if (event.target.classList.contains('delete-btn')) {
        deleteTask(event.target.parentElement);
    } else if (event.target.tagName === 'LI') {
        toggleTaskCompletion(event.target);
    }
});

function addTask(taskText) {
    const li = document.createElement('li');
    li.textContent = taskText;
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.classList.add('delete-btn');
    li.appendChild(deleteBtn);
    taskList.appendChild(li);
    saveTasks();
}

function deleteTask(taskElement) {
    taskElement.remove();
    saveTasks();
}

function toggleTaskCompletion(taskElement) {
    taskElement.classList.toggle('completed');
    saveTasks();
}

function saveTasks() {
    const tasks = [];
    taskList.querySelectorAll('li').forEach(task => {
        tasks.push({
            text: task.firstChild.textContent,
            completed: task.classList.contains('completed'),
        });
    });
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

function loadTasks() {
    const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
    tasks.forEach(task => {
        const li = document.createElement('li');
        li.textContent = task.text;
        if (task.completed) {
            li.classList.add('completed');
        }
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.classList.add('delete-btn');
        li.appendChild(deleteBtn);
        taskList.appendChild(li);
    });
}
