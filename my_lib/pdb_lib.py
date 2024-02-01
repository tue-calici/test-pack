
import pathlib
from typing import Union, List
from .file_lib import load_file_to_list_str


LIST_ELEMENT_ION = ['AG', 'AL', 'BE', 'CA', 'CD', 'CL', 'CO', 'CR', 'CU', 'FE', 'GA', 'HE', 'IN ', 'LI', 'MG', 'MN',
                    'NE', 'NI', 'PB', 'K', 'RH', 'RB', 'SC', 'SN', 'NA', 'SR', 'TI', 'V2', 'V3', 'Y3', 'ZN', 'SE', 'BR', 'P', 'S', 'MO']
LIST_ELEMENT_REMOVE = ['AU', 'BA', 'BI', 'CE', 'CS', 'DY', 'ER', 'EU', 'GD', 'HG', 'HO', 'LA',
                       'LU', 'ND', 'PD', 'PM', 'PR', 'PT', 'PU', 'RA', 'SM', 'TB', 'TL', 'TU', 'U1', 'U3', 'YB']


class PdbRecord(object):
    record_name: str  # 1..6
    serial: int  # 7..11
    __atom_name_1: str  # 13 - 14  - right justified
    __atom_name_2: str  # 15 - 16 - left justified
    alt_loc: str  # 17
    residue_name: str  # 18..20
    chain_id: str  # 22
    residue_seq: int  # 23..26
    i_code: str  # 27
    x: float  # 31..38
    y: float  # 39..46
    z: float  # 47..54
    occupancy: str  # 55..60
    temp_factor: str  # 61..66
    seg_id: str  # 73..76
    element: str  # 77..78
    charge: str  # 79..80
    data: str
    org_data: str

    def __init__(self, data: str):
        if not data or len(data) < 78:
            raise ValueError(f"This record is not PDB record - length error={len(data)}")
        if not data[6:11].strip().isdigit() or not data[22:26].strip().isdigit():
            raise ValueError("This record is not PDB record - number error.")

        self.record_name = data[0:6].strip()
        if self.record_name not in ['ATOM', 'HETATM']:
            raise ValueError("This record is not PDB record - record name error.")
        self.data = self.org_data = data
        self.serial = int(data[6:11])
        self.__atom_name_1 = data[12:14].strip()
        self.__atom_name_2 = data[14:16].strip()
        self.alt_loc = data[16:17].strip()
        self.residue_name = data[17:20].strip()
        self.chain_id = data[21:22].strip()
        self.residue_seq = int(data[22:26])
        self.i_code = data[26:27].strip()
        try:
            self.x = float(data[30:38])
            self.y = float(data[38:46])
            self.z = float(data[46:54])
            self.occupancy = float(data[54:60])
            self.temp_factor = float(data[60:66])
        except Exception as ex:
            raise ValueError("This record is not PDB record - number error.")

        self.seg_id = data[72:76].strip()
        self.element = data[76:78].strip()
        self.charge = data[78:80].strip() if len(data) > 78 else ''

    @property
    def is_atom(self) -> bool:
        return self.record_name and self.record_name == 'ATOM'

    @property
    def is_hetatm(self) -> bool:
        return self.record_name and self.record_name == 'HETATM'

    @property
    def is_co_factor(self) -> bool:
        return self.is_hetatm

    @property
    def is_remove_ion(self) -> bool:
        return self.element in LIST_ELEMENT_REMOVE

    @property
    def is_remove_item(self) -> bool:
        return self.is_remove_ion or self.__residue_name == 'HOH'

    @property
    def is_ion(self) -> bool:
        return self.element in LIST_ELEMENT_ION

    @property
    def is_ion_need_change_residue_name(self) -> bool:
        """This record is ion and need to change atom_name = element
        """
        return self.is_ion and self.__residue_name != self.element

    @property
    def file_name(self) -> bool:
        return f'{self.__residue_name}-{self.residue_seq:04d}.pdb'

    @property
    def atom_name_full(self):
        return self.__atom_name_1.rjust(2) + self.__atom_name_2.ljust(2)

    @property
    def atom_name(self):
        return self.atom_name_full.strip()

    @atom_name.setter
    def atom_name(self, atom_name: str):
        if len(atom_name) <= 2:
            self.__atom_name_1 = atom_name
        else:
            self.__atom_name_1 = atom_name[:2]
            self.__atom_name_2 = atom_name[2:]
        self.reset_data()

    def __str__(self) -> str:
        return self.data

    def __repr__(self) -> str:
        return self.data

    def reset_data(self):
        self.data = (
            self.record_name.ljust(6)
            + f"{self.serial:5d}"
            + ' '
            + self.atom_name_full
            + self.alt_loc.ljust(1)
            + self.residue_name.rjust(3)
            + ' '
            + self.chain_id.ljust(1)
            + f"{self.__residue_seq:4d}"
            + (' ' * 3)
            + self.i_code.ljust(1)
            + f"{self.x:8.3f}"
            + f"{self.y:8.3f}"
            + f"{self.z:8.3f}"
            + f"{self.occupancy:6.2f}"
            + f"{self.temp_factor:6.2f}"
            + (' ' * 6)
            + self.seg_id.ljust(4)
            + self.element.rjust(2)
            + (self.charge if self.charge else '')
        )


def load_pdb_file(file_path: Union[pathlib.Path, str]) -> List[PdbRecord]:
    data = load_file_to_list_str(file_path)
    ret = []
    for _ in data:
        try:
            ret.append(PdbRecord(_))
        except ValueError:
            # Ignore ValueError
            pass
    return ret
