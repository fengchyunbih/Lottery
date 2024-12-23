function drawing_groups_onchange_handler(event) {
    const drawing_group = parseInt(event.target.value, 10);
    switch (drawing_group) {
        case 1:
            location.href = "/senior_member";
            break;
        case 2:
            location.href = "/junior_member";
            break;
        case 3:
            location.href = "/new_member";
            break;
        default:
            location.href = `/gifts?drawing_group=${drawing_group}`;
    }
}
