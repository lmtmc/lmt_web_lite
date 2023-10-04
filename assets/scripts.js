if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    make_draggable: function(is_open) {
        if(is_open) {
            var modal = document.getElementById('draggable-modal');
            var header = document.getElementById('draggable-header');
            var startPosX = 0, startPosY = 0, modalStartX = 0, modalStartY = 0;
            var isDragging = false;

            if (modal) {
                modal.addEventListener('mousedown', function (event) {
                    isDragging = true;

                    // Record the initial position of the mouse and the modal
                    startPosX = event.clientX;
                    startPosY = event.clientY;
                    modalStartX = modal.offsetLeft;
                    modalStartY = modal.offsetTop;

                    // Attach the mousemove and mouseup listeners
                    document.addEventListener('mousemove', onMouseMove);
                    document.addEventListener('mouseup', onMouseUp);
                });
            }
        }
            function onMouseMove(event) {
                if (!isDragging) return;
                //calculate the new position
                var dx = event.clientX - startPosX;
                var dy = event.clientY - startPosY;

                modal.style.left = (modalStartX + dx) + 'px';
                modal.style.top = (modalStartY + dy) + 'px';
            }

            function onMouseUp() {
                isDragging = false;
                //Detach the mousemove and mouseup listeners
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            }

        return window.dash_clientside.no_update;
    }
}