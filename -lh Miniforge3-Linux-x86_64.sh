[33mcommit 42b049571f94008001d8149680d549380def15b2[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mfeature/marcin-db-setup[m[33m)[m
Author: MarcinLawrenc <marcin.m.lawrenc@gmail.com>
Date:   Mon Sep 1 18:00:41 2025 +0200

    Add database setup, user management, and enhanced frontend features

 Miniforge3-Linux-x86_64.sh                         | 356196 [32m+++++++++++++++++[m
 README.md                                          |    388 [32m+[m[31m-[m
 alembic.ini                                        |     74 [32m+[m[31m-[m
 alembic/env.py                                     |    182 [32m+[m[31m-[m
 alembic/script.py.mako                             |     52 [32m+[m[31m-[m
 alembic/versions/3cdc333b3266_units_and_leases.py  |    132 [32m+[m[31m-[m
 .../versions/445f7ca1bb11_create_files_table.py    |     68 [32m+[m[31m-[m
 alembic/versions/62e407a50105_adde_properties.py   |     84 [32m+[m[31m-[m
 alembic/versions/6636d8c9b16f_added_user_roles.py  |     76 [32m+[m[31m-[m
 alembic/versions/91506d06f6fd_add_admin_user.py    |     42 [32m+[m
 alembic/versions/ef2910566747_add_users_table.py   |     78 [32m+[m[31m-[m
 api/__init__.py                                    |      2 [32m+[m[31m-[m
 api/core/config.py                                 |     44 [32m+[m[31m-[m
 api/core/database.py                               |     52 [32m+[m[31m-[m
 api/core/exceptions.py                             |     70 [32m+[m[31m-[m
 api/core/logging.py                                |     40 [32m+[m[31m-[m
 api/core/security.py                               |    126 [32m+[m[31m-[m
 api/main.py                                        |     86 [32m+[m[31m-[m
 api/src/enums/__init__.py                          |      6 [32m+[m[31m-[m
 api/src/enums/enums_user_role.py                   |     14 [32m+[m[31m-[m
 api/src/leases/models.py                           |     50 [32m+[m[31m-[m
 api/src/leases/repository.py                       |    260 [32m+[m[31m-[m
 api/src/leases/routes.py                           |    126 [32m+[m[31m-[m
 api/src/leases/schemas.py                          |     90 [32m+[m[31m-[m
 api/src/leases/service.py                          |    110 [32m+[m[31m-[m
 api/src/properties/models.py                       |     34 [32m+[m[31m-[m
 api/src/properties/repository.py                   |    228 [32m+[m[31m-[m
 api/src/properties/routes.py                       |    204 [32m+[m[31m-[m
 api/src/properties/schemas.py                      |     74 [32m+[m[31m-[m
 api/src/properties/service.py                      |    136 [32m+[m[31m-[m
 api/src/units/models.py                            |     40 [32m+[m[31m-[m
 api/src/units/repository.py                        |    194 [32m+[m[31m-[m
 api/src/units/routes.py                            |    166 [32m+[m[31m-[m
 api/src/units/schemas.py                           |     70 [32m+[m[31m-[m
 api/src/units/service.py                           |    148 [32m+[m[31m-[m
 api/src/users/models.py                            |     48 [32m+[m[31m-[m
 api/src/users/repository.py                        |    162 [32m+[m[31m-[m
 api/src/users/routes.py                            |     92 [32m+[m[31m-[m
 api/src/users/schemas.py                           |     70 [32m+[m[31m-[m
 api/src/users/service.py                           |     98 [32m+[m[31m-[m
 api/upload.py                                      |    112 [32m+[m[31m-[m
 api/utils/migrations.py                            |     78 [32m+[m[31m-[m
 client/.gitignore                                  |     48 [32m+[m[31m-[m
 client/README.md                                   |    150 [32m+[m[31m-[m
 client/app.config.ts                               |     22 [32m+[m[31m-[m
 client/app.vue                                     |     14 [32m+[m[31m-[m
 client/assets/styles/main.css                      |     14 [32m+[m[31m-[m
 client/components/AppFooter.vue         