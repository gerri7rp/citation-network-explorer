CREATE CONSTRAINT id_camp_estudi_unique IF NOT EXISTS
FOR (c:Camp_Estudi)
REQUIRE c.id IS NODE KEY 