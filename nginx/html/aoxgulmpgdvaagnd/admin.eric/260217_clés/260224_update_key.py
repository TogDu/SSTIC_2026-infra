from test_arch import make_arch
from create_pkg import BlobType

from GEMINI.HSM import get_public, get_sdata
from GEMINI.HSM.internal import export_private_internal


def cmd_update_key(pub_key, priv_key):
    #pour vérifier une signature, diode_dst à besoin de la privée et de la publique ?
    # test de (r, s) == lobster256.sign(data, priv) ??? 
    # => mais du coup la publique sert à rien ? 
    # => vérifier avec Ernest ou Michel

    data = pub_key + priv_key
    return { "type": BlobType.UPDATE_SIG_KEY, "size":len(data), "data":data }


prod_key_pub = get_public("LOBSTER256", "PRODUCTION PCA 2026")
prod_key_priv = export_private_internal("LOBSTER256","PRODUCTION PCA 2026")

#sauvegarder la clé publique pour tracabilité et tests
with open('./clés/PROD/prod_public_key', 'wb') as f:
    f.write(prod_key_pub)

#######################################################################
#!!!!! LA CLE PRIVEE NE DOIT JAMAIS ETRE ECRITE DANS UN FICHIER !!!!
# with open('./clés/PROD/prod_private_key', 'wb') as f:
#     f.write(prod_key_priv)
#######################################################################

commands = [cmd_update_key(prod_key_pub, prod_key_priv)]
tags = ["RELEASE", "SETUP_KEY", "ARCHIVE", "SSTIC2026" ]

#make_arch
#   pkg de jean
#       commands:       listes des commandes à inclure
#       destination:    où envoyer les données => identifiant unique du système SAFE cible, peut être récupéré dans les secured data du HSM
#       tags:           debug pour logs
#       private_key_id  identifiant de la clé de signature
data = make_arch(commands, get_sdata("ARCHIVE:id_SAFE_817"), tags, "SAFE PREPROD 2026")
open("./out/prod_maj_key.sa", "wb").write(data)