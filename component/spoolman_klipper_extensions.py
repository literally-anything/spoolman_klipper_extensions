import logging
from typing import TYPE_CHECKING, Any
# noinspection PyUnresolvedReferences
from ..common import WebRequest, RequestType
# noinspection PyUnresolvedReferences
from .spoolman import SpoolManager

if TYPE_CHECKING:
    from moonraker.moonraker.confighelper import ConfigHelper, Server
    from moonraker.moonraker.components.klippy_apis import KlippyAPI
    from moonraker.moonraker.components.spoolman import SpoolManager
    from moonraker.moonraker.common import WebRequest, RequestType

PREHEAT_MACRO_NAME = 'SMART_PREHEAT'
PREHEAT_SETUP_MACRO_NAME = '_SETUP_SMART_PREHEAT'
PREHEAT_DEFAULT_EXTRUDER_TEMP = 200
PREHEAT_DEFAULT_BED_TEMP = 60


class SpoolmanKlipperExtensions:
    def __init__(self, confighelper: 'ConfigHelper') -> None:
        self._confighelper: 'ConfigHelper' = confighelper
        self._server: 'Server' = self._confighelper.get_server()
        self._klippy_api: 'KlippyAPI' = self._server.lookup_component('klippy_apis')
        self._spoolman: SpoolManager | None = None

        self.preheat_default_extruder_temp = self._confighelper.getint(
            'preheat_default_extruder_temp',
            PREHEAT_DEFAULT_EXTRUDER_TEMP
        )
        self.preheat_default_bed_temp = self._confighelper.getint(
            'preheat_default_bed_temp',
            PREHEAT_DEFAULT_BED_TEMP
        )

        self.preheat_extruder_temp = self.preheat_default_extruder_temp
        self.preheat_bed_temp = self.preheat_default_bed_temp

        self._server.register_event_handler('server:klippy_ready', self._handle_klippy_ready)
        self._server.register_event_handler('spoolman:spoolman_status_changed', self._handle_spoolman_status)
        self._server.register_event_handler('spoolman:active_spool_set', self._handle_spool_change)

    async def _handle_klippy_ready(self) -> None:
        await self.update_preheat_temps()

    async def _handle_spoolman_status(self, spoolman_status: dict[str, Any]) -> None:
        state = spoolman_status.get('spoolman_connected', None)
        if state is not None:
            if state:
                self._spoolman = self._server.lookup_component('spoolman')

                if self._spoolman.spool_id is not None:
                    await self._handle_spool_change({'spool_id': self._spoolman.spool_id})
            else:
                self._spoolman = None

    async def _handle_spool_change(self, spool_info: dict[str, Any]) -> None:
        spool_id: int | None = spool_info.get('spool_id', None)
        if self._spoolman is not None:
            if spool_id is not None:
                spool_request = WebRequest(
                    '/server/spoolman/proxy',
                    {
                        'path': f'/v1/spool/{spool_id}',
                        'request_method': 'GET',
                        'use_v2_response': True
                    },
                    RequestType.POST
                )
                # noinspection PyProtectedMember
                spool_response = await self._spoolman._proxy_spoolman_request(spool_request)
                filament = spool_response.get('filament', {})
            else:
                filament = {}

            self.preheat_extruder_temp = filament.get('settings_extruder_temp', self.preheat_default_extruder_temp)
            self.preheat_bed_temp = filament.get('settings_bed_temp', self.preheat_default_bed_temp)

            if self._klippy_api.klippy.is_connected():
                klipper_objects = await self._klippy_api.get_object_list([])
                if f'gcode_macro {PREHEAT_SETUP_MACRO_NAME}' in klipper_objects:
                    await self.update_preheat_temps()
            else:
                logging.warning('Received spool change event while klippy is not connected')
        else:
            logging.error('Received spool change event, but spoolman is not connected')

    async def update_preheat_temps(self) -> None:
        gcode = f'{PREHEAT_SETUP_MACRO_NAME} EXTRUDER={self.preheat_extruder_temp} BED={self.preheat_bed_temp}'
        await self._klippy_api.run_gcode(gcode)


def load_component(config: 'ConfigHelper') -> SpoolmanKlipperExtensions:
    return SpoolmanKlipperExtensions(config)
