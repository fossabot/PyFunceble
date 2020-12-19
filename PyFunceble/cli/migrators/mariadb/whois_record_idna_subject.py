"""
The tool to check the availability or syntax of domain, IP or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provides our WHOIS record migrator.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.github.io/#/special-thanks

Contributors:
    https://pyfunceble.github.io/#/contributors

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io/en/dev/

Project homepage:
    https://pyfunceble.github.io/

License:
::


    Copyright 2017, 2018, 2019, 2020 Nissar Chababy

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import domain2idna
import sqlalchemy

import PyFunceble.cli.factory
from PyFunceble.cli.migrators.mariadb.base import MariaDBMigratorBase
from PyFunceble.database.sqlalchemy.all_schemas import WhoisRecord


class WhoisRecordIDNASubjectMigrator(MariaDBMigratorBase):
    """
    Provides the interface which provides the completion of the missing
    IDNA subject column.
    """

    @property
    def authorized(self) -> bool:
        """
        Provides the authorization to process.
        """

        if PyFunceble.cli.facility.CredentialLoader.is_already_loaded():
            with PyFunceble.cli.factory.DBSession.get_new_db_session() as db_session:
                # pylint: disable=singleton-comparison
                return (
                    db_session.query(WhoisRecord)
                    .filter(WhoisRecord.idna_subject == None)
                    .with_entities(sqlalchemy.func.count())
                    .scalar()
                    > 0
                )
        return False

    @MariaDBMigratorBase.execute_if_authorized(None)
    def migrate(self) -> "WhoisRecordIDNASubjectMigrator":
        with PyFunceble.cli.factory.DBSession.get_new_db_session() as db_session:
            # pylint: disable=singleton-comparison
            for row in db_session.query(WhoisRecord).filter(
                WhoisRecord.idna_subject == None
            ):
                row.idna_subject = domain2idna.domain2idna(row.subject)

                db_session.add(row)
                db_session.commit()

        return self