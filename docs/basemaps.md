# Подложки

Provider contract: `{ id, name, type, tiles?, styleUrl?, attribution, minzoom?, maxzoom? }`. OSM endpoint задаётся `NEXT_PUBLIC_OSM_TILES`; публичный `tile.openstreetmap.org` подходит только для разработки и умеренного интерактивного использования с attribution.

COSMO/TOPO не имеют зафиксированного в официальных источниках публичного endpoint проекта. Поэтому поля env пусты, провайдеры disabled. Для подключения укажите легальный XYZ/WMTS или vector style URL, token способом провайдера, attribution и zoom limits. Секретный token не коммитьте.

