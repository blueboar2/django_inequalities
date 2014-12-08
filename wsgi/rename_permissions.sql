\connect inequality
update auth_permission set name='Может добавить студента' where codename='add_student';
update auth_permission set name='Может изменить студента' where codename='change_student';
update auth_permission set name='Может удалить студента' where codename='delete_student';
update auth_permission set name='Может добавить преподавателя' where codename='add_teacher';
update auth_permission set name='Может изменить преподавателя' where codename='change_teacher';
update auth_permission set name='Может удалить преподавателя' where codename='delete_teacher';
