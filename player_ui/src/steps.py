import hashlib
from dataclasses import dataclass


@dataclass
class Step:
    description: str
    template_file: str
    inputs: str
    flag_hash: str
    diode_dest: bool


def hash_flag(flag: str) -> str:
    return hashlib.sha256(flag.encode()).hexdigest()

STEP1_FILER_PATH = "/aoxgulmpgdvaagnd"

STEPS = {
    "5bc47fb5b3fb831ee96884387fd16871": Step(
        description="""Bienvenue dans la deuxième étape du challenge du SSTIC. Dans cette deuxième étape, vous devez vous attaquer à la diode source qui expose un serveur SFTP""",
        template_file="step2.html",
        inputs=["a core dump : invastigated by Jean", "SFTP credentials : on a technical documentation ?"],
        flag_hash="1005ffb3c63882b739d76526eca62cfabc56049db199b838cf6179d887b04d04",
        diode_dest=False,
    ),
    "df4bddd435bb9b4cf0896565705b9b3b": Step(
        description="""Bienvenue dans la troisième étape du challenge du SSTIC. Une nouvelle cible partie de votre scope : la diode de destination sur laquelle sont envoyés les fichiers. Un flux VNC vous est fourni afin d'espionner l'écrant de la diode. Veuillez noter que le VNC en lui-même est en dehors du périmètre du challenge.""",
        template_file="step3.html",
        inputs=[
                "lobster project backup on Michel home", 
                "a recording of a call between Michel and Ernest",
                "Eric was working on a script called diode_dst",
                "on diode_src archive folder : updates containing binaries and keys"
                ],
        flag_hash="a3a1110ec6f7871b195f630a992bd658f08866a48fd0de9e2bf961f6884b7165",
        diode_dest=True,
    ),
    "48df3610c3412eb5f513de714fc28601": Step(
        description="""Bienvenue dans la quatrième étape du challenge du SSTIC""",
        template_file="step4.html",
        inputs=[
            "binaries stored by Jean",
            "a monitoring stream"
            ],
        flag_hash="c2d789155e8e1c0f9650809d4c5d20c7f23f5201687e1b8105aff3f6918c8e72",
        diode_dest=True,
    ),
    "fd0c9dd1f12907bf25f4fd7af0bd83e5": Step(
        description="""Bienvenue dans la cinquième étape du challenge du SSTIC""",
        template_file="step5.html",
        inputs=["a user database to extract"],
        flag_hash="99d9f74bec682698b76235375ae04463756c18a7f50f301a24680835d848cc9f",
        diode_dest=True,
    ),
}
