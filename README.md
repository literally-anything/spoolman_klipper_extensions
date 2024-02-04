# Install
```bash
cd ~
git clone https://github.com/literally-anything/spoolman_klipper_extensions.git
cd ~/spoolman_klipper_extensions
bash scripts/install.sh
```
Add this to your `printer.cfg`:
```ini
# printer.cfg

[include spoolman_klipper_extensions.cfg]
```
Add this to your `moonraker.cfg` to enable the component:
```ini
# moonraker.cfg

[spoolman_klipper_extensions]
```
Add this to your `moonraker.cfg` to allow updating automatically:
```ini
# moonraker.cfg

[update_manager spoolman_klipper_extensions]
type: git_repo
primary_branch: master
path: ~/spoolman_klipper_extensions
origin: https://github.com/literally-anything/spoolman_klipper_extensions.git
managed_services: klipper moonraker
```
