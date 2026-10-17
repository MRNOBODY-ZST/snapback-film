$ErrorActionPreference = 'Stop'
# OWN_DESIGN bench-carrier interface coordinates; not vendor footprints or an RB67 fit model.
$pinSignals = @('GND','LOGIC_3V3_REF','A_IN1','A_IN2','B_IN1','B_IN2','A_ARM','B_ARM',
  'PACK_PRESENT_N','DOOR_CLOSED_N','DARK_SLIDE_INSERTED_N','PICKUP_HOME_N','ROLLER_ENTRY_N','FILM_EXIT_N',
  'ADC_I_A','ADC_I_B','ADC_VBAT','ADC_VM','A_FAULT_N','B_FAULT_N','A_STALL_N','B_STALL_N',
  'BTN_EJECT_N','BTN_LOAD_N','LED_READY_DRV','LED_FAULT_DRV','CHARGE_PAUSE','CHARGE_PAUSE_ACK',
  'CHG_STAT1_N','CHG_STAT2_N','VBUS_PRESENT','SENSOR_PWR_EN','EMITTER_EN','KILL_REQUEST','KILL_SENSE',
  'HW_ARM_AUTH','MCU_TX','MCU_RX','I2C_SCL','I2C_SDA','SWDIO','SWCLK','NRST','HW_WDI',
  'CAPTURE_PROOF','REVERSE_POSITION_VALID','REVERSE_LIMIT_REACHED','GND')
$outputs = @('A_IN1','A_IN2','B_IN1','B_IN2','A_ARM','B_ARM','LED_READY_DRV','LED_FAULT_DRV',
 'CHARGE_PAUSE','SENSOR_PWR_EN','EMITTER_EN','KILL_REQUEST','MCU_TX','HW_WDI')
$analogInputs = @('ADC_I_A','ADC_I_B','ADC_VBAT','ADC_VM')
$bidirectional = @('I2C_SCL','I2C_SDA','SWDIO')
$controlPins = for ($i=0; $i -lt $pinSignals.Count; $i++) {
    $s=$pinSignals[$i]
    $direction = if($s -eq 'GND' -or $s -eq 'LOGIC_3V3_REF') {'reference'} elseif($s -in $outputs) {'controller_output'} elseif($s -in $bidirectional) {'bidirectional'} else {'controller_input'}
    [ordered]@{pin=$i+1;signal=$s;direction=$direction;electrical_type=$(if($s -in $analogInputs){'ADC_SCALED_CALIBRATION_REQUIRED'}elseif($direction -eq 'reference'){'reference'}else{'3V3_LOGIC'});
      x_mm=[Math]::Round(15.79+[Math]::Floor($i/2)*2.54,2);y_mm=$(if($i%2 -eq 0){57.73}else{60.27});z_mm=0;scope='OWN_DESIGN';mcu_pad=$null}
}
function New-Port([string]$ref,[double]$x,[double]$y,[double]$pitch,[string[]]$signals,[string]$role) {
    $pins = for($i=0;$i -lt $signals.Count;$i++) {
        [ordered]@{pin=$i+1;signal=$signals[$i];x_mm=[Math]::Round($x-($signals.Count-1)*$pitch/2+$i*$pitch,2);y_mm=$y;z_mm=0;scope='OWN_DESIGN'}
    }
    [ordered]@{reference=$ref;role=$role;center_mm=@($x,$y,0);rows=1;pitch_mm=$pitch;
      numbering='pin1 at lowest X; increases +X, top view';mating_direction=@(0,0,1);part_number=$null;
      part_status='PART_SELECTION_REQUIRED';terminal_current_rating_a=$null;envelope_status='ESTIMATED_NOT_VENDOR_FOOTPRINT';pins=@($pins)}
}
$ports=@(
 (New-Port 'J_MA' 12 30 5.08 @('A_OUT1','A_OUT2') 'motor A switched outputs; neither is GND'),
 (New-Port 'J_MB' 12 42 5.08 @('B_OUT1','B_OUT2') 'motor B switched outputs; neither is GND'),
 (New-Port 'J_VM' 12 18 5.08 @('VM_EXT','POWER_GND') 'current-limited external bench motor supply'),
 (New-Port 'J_BAT' 27 10 5.08 @('PROTECTED_P_PLUS','PROTECTED_P_MINUS','CELL_NTC') 'protected 1S pack; not raw cell'),
 (New-Port 'J_LOGIC' 27 18 5.08 @('LOGIC_3V3_IN','GND') 'external regulated 3V3 bench supply; never raw cell/SYS'),
 (New-Port 'J_SYS_MON' 27 26 5.08 @('CHARGER_SYS','GND') 'power-path measurement output; not linked to VM/3V3 by default'),
 (New-Port 'J_UI' 54 12 2.54 @('GND','BTN_EJECT_N','BTN_LOAD_N','LED_READY_DRV','LED_FAULT_DRV') 'buttons and current-limited LED drivers'),
 (New-Port 'J_UART' 54 22 2.54 @('GND','LOGIC_3V3_REF','MCU_TX','MCU_RX') 'external 3V3 USB-UART; reference only, no backfeed'),
 (New-Port 'J_SWD' 54 32 2.54 @('GND','LOGIC_3V3_REF','SWDIO','SWCLK','NRST') 'optional STM32 daughterboard SWD'),
 (New-Port 'J_ARM' 54 42 2.54 @('GND','HW_ARM_AUTH','KILL_SENSE','MANUAL_KILL_CLEAR_N') 'physical ARM authorization and manual latch clear'),
 (New-Port 'J_PROOF' 32 47 2.54 @('GND','CAPTURE_PROOF','REVERSE_POSITION_VALID','REVERSE_LIMIT_REACHED') 'independent calibrated transport/position evidence'),
 (New-Port 'J_DISPLAY' 32 39 2.54 @('GND','LOGIC_3V3_REF','I2C_SCL','I2C_SDA') 'optional display or diagnosed-sensor interface')
)
$sensorNames=@('PACK_PRESENT_N','DOOR_CLOSED_N','DARK_SLIDE_INSERTED_N','PICKUP_HOME_N','ROLLER_ENTRY_N','FILM_EXIT_N')
for($i=0;$i -lt 6;$i++) { $ports += New-Port "J_S$i" 78 (15+7*$i) 2.54 @('GND',$sensorNames[$i],'SENSOR_3V3') '3V3 digital sensor; pin2 active-low; optical emitter forbidden by default' }
$ports += [ordered]@{reference='J_CTRL';role='external controller daughterboard, logical pins not MCU package pads';center_mm=@(45,59,0);rows=2;columns=24;pitch_mm=2.54;
  numbering='odd pins at Y57.73; even at Y60.27; columns increase +X; pin1 X15.79';mating_direction=@(0,0,1);
  part_number=$null;part_status='PART_SELECTION_REQUIRED';terminal_current_rating_a=$null;envelope_status='ESTIMATED_NOT_VENDOR_FOOTPRINT';pins=@($controlPins)}
$ports += [ordered]@{reference='J_USB';role='5V USB-C sink charging only; external UART is bench debug path';center_mm=@(45,3,0);
  mating_direction=@(0,-1,0);part_number=$null;part_status='PART_SELECTION_REQUIRED';
  footprint_pin_coordinates=$null;envelope_mm=@(11,8);envelope_status='ESTIMATED_NOT_VENDOR_FOOTPRINT';
  usb_connections=[ordered]@{VBUS='USB_5V';GND='GND';CC1='independent 5.1k Rd to GND';CC2='independent 5.1k Rd to GND';D_PLUS='NC charging-only bench';D_MINUS='NC charging-only bench';shield='ESD/chassis policy pending'}}
$unknowns=[ordered]@{}
foreach($name in @('motor_a_vm_v','motor_b_vm_v','motor_a_continuous_current_a','motor_b_continuous_current_a',
 'motor_a_jam_current_a','motor_b_jam_current_a','motor_a_hard_current_a','motor_b_hard_current_a',
 'motor_a_duty','motor_b_duty','motor_a_reverse_duty','current_adc_gain_a_per_v','current_adc_gain_b_per_v',
 'current_adc_offset_a_v','current_adc_offset_b_v','vm_adc_scale','battery_start_voltage_v','battery_abort_voltage_v',
 'battery_capacity_ah','battery_peak_current_a','battery_continuous_current_a','usb_source_budget_a','charge_current_a',
 'watchdog_timeout_ms','debounce_ms','pickup_home_leave_timeout_ms','entry_timeout_ms','capture_timeout_ms',
 'exit_enter_timeout_ms','exit_clear_timeout_ms','home_return_timeout_ms','total_cycle_timeout_ms','startup_blank_ms','jam_dwell_ms','reverse_max_ms')) {
  $unknowns[$name]=[ordered]@{value=$null;status='UNKNOWN';source='MEASUREMENT_REQUIRED_OR_PART_SELECTION_REQUIRED'}
}
$model=[ordered]@{
 schema_version=1;artifact='R0 independent bench carrier interface';not_final_back_pcb=$true;pcb_author='user';hardware_validated=$false;film_validated=$false;
 units=[ordered]@{length='mm';voltage='V';current='A';time='ms'};
 provenance_classes=@('VERIFIED_MEASUREMENT','MANUFACTURER_SPEC','RELIABLE_SOURCE','DERIVED','ESTIMATED','UNKNOWN');
 provenance_defaults=[ordered]@{
   geometry=[ordered]@{applies_to=@('board.width_mm','board.height_mm','board.thickness_mm','board.mounting_holes[*]','connectors[*].center_mm','connectors[*].pitch_mm','connectors[*].envelope_mm','connectors[*].mating_direction');status='ESTIMATED';source='OWN_DESIGN';note='designer-selected independent bench geometry, not measured original camera dimensions'};
   pin_coordinates=[ordered]@{applies_to='connectors[*].pins[*].x_mm/y_mm/z_mm';status='DERIVED';source='single row: centerX-(N-1)*pitch/2+(pin-1)*pitch; J_CTRL: X15.79+floor((pin-1)/2)*2.54, oddY57.73/evenY60.27, Z0'};
   pin_assignment=[ordered]@{applies_to='connectors[*].pins[*].pin/signal/direction/electrical_type';status='ESTIMATED';source='OWN_DESIGN_LOGICAL_INTERFACE_CONTRACT';note='fixed R0 logical mapping, not MCU/vendor footprint pad numbering'};
   unknown=[ordered]@{applies_to=@('unknowns[*]','connectors[*].part_number','connectors[*].terminal_current_rating_a','connectors[*].pins[*].mcu_pad','coordinate_system.installed_back_transform','analog.vm_divider_values');status='UNKNOWN';source='MEASUREMENT_REQUIRED_OR_PART_SELECTION_REQUIRED'};
   candidate_facts=[ordered]@{applies_to='candidates[*].limit_note';status='MANUFACTURER_SPEC';source='each candidate.source URL';note='component constraints, not measured application performance'};
   design_electrical=[ordered]@{applies_to=@('logic.nominal_v','logic.bench_supply_tolerance_percent','analog.vbat_divider','analog.ADC_full_scale_v');status='ESTIMATED';source='OWN_DESIGN';note='must be checked/calibrated, not hardware enable thresholds'}
 };
 coordinate_system=[ordered]@{origin='board lower-left corner viewed from component side';x='+right';y='+up';z='+out of component side';installed_back_transform=$null;installed_back_transform_status='MEASUREMENT_REQUIRED'};
 board=[ordered]@{width_mm=90;height_mm=70;thickness_mm=1.6;outline_scope='OWN_DESIGN_BENCH_ONLY';outline_provenance='ESTIMATED';thickness_provenance='ESTIMATED';thickness_source='OWN_DESIGN_FABRICATION_CHOICE';installed_fit='UNVERIFIED';mounting_holes=@(
  [ordered]@{id='H1';x_mm=4;y_mm=4;diameter_mm=3.2;status='ESTIMATED';source='OWN_DESIGN'},[ordered]@{id='H2';x_mm=86;y_mm=4;diameter_mm=3.2;status='ESTIMATED';source='OWN_DESIGN'},
  [ordered]@{id='H3';x_mm=86;y_mm=66;diameter_mm=3.2;status='ESTIMATED';source='OWN_DESIGN'},[ordered]@{id='H4';x_mm=4;y_mm=66;diameter_mm=3.2;status='ESTIMATED';source='OWN_DESIGN'})};
 connectors=$ports;logic=[ordered]@{nominal_v=3.3;status='ESTIMATED';source='OWN_DESIGN';sensor_active_low=$true;GPIO_output_default='LOW except CHARGE_PAUSE HIGH; hardware kill defaults latched';arm_default='LOW';emitter_default='OFF';
  supply_port='J_LOGIC';bench_supply_tolerance_percent=5;bench_supply_status='OWN_DESIGN_INPUT_REQUIREMENT';J_CTRL_pin2='reference only; no power backfeed';
  arm_gate='A/B_ARM AND HW_ARM_AUTH AND raw_DOOR_OK AND RAIL_OK AND watchdog_OK AND NOT KILL_LATCHED';
  kill_clear='physical momentary only after inspection; ARM_AUTH=0, A_ARM=B_ARM=0, door closed, rails healthy; never firmware automatic';
  sensor_health='three-wire active-low signal alone cannot prove open/short health; independent diagnosed HAL required'};
 analog=[ordered]@{vbat_divider=[ordered]@{upper_ohm=150000;lower_ohm=100000;nominal_adc_v_per_battery_v=0.4;status='ESTIMATED';source='OWN_DESIGN_PROPOSED';acquisition_calibrated=$false};
  current_channels='independent A and B ADC signals, not battery current';vm_divider_values=$null;battery_current_channel='external instrument only; not sum of motor PWM currents';ADC_full_scale_v=3.3;ADC_full_scale_status='OWN_DESIGN_INTERFACE_TARGET_NOT_MEASURED'};
 candidates=@(
  [ordered]@{part='DRV8213RTE x2';purpose='independent bridges/current mirror';source='https://www.ti.com/lit/ds/symlink/drv8213.pdf';limit_note='4A peak only, continuous thermal/current limit unverified; external input gating, no fabricated nSLEEP'},
  [ordered]@{part='BQ25185';purpose='1S charger power-path';source='https://www.ti.com/lit/ds/symlink/bq25185.pdf';limit_note='up to 1A charge; SYS typically 4.5V with USB; BAT-to-SYS recommended 3.125A max; not motor qualification'},
  [ordered]@{part='BQ29700 + matched MOSFETs or traceable protected pack';purpose='independent cell protection';source='https://www.ti.com/lit/ds/symlink/bq2970.pdf';limit_note='cell/threshold/FET selection pending'},
  [ordered]@{part='STM32C031C6 candidate daughterboard';purpose='controller ADC/PWM/UART/SWD';source='https://www.st.com/resource/en/datasheet/stm32c031c6.pdf';limit_note='no final MCU pad/pinmux assignment; not native USB'});
 unknowns=$unknowns
}
$jsonPath=Join-Path $PSScriptRoot 'R0_bench-interface.json'
$utf8NoBom=[Text.UTF8Encoding]::new($false)
[IO.File]::WriteAllText($jsonPath,($model | ConvertTo-Json -Depth 15),$utf8NoBom)
$svg=@'
<svg xmlns="http://www.w3.org/2000/svg" width="110mm" height="112mm" viewBox="-10 -18 110 112">
<title>R0 independent bench carrier — OWN_DESIGN, no RB67 fit claim</title>
<desc>Dimensions in mm. Connector circles are interface pin centres, not manufacturer footprints. Y coordinates are transformed from the component-side lower-left-origin coordinate contract.</desc>
<style>text{font-family:Arial,sans-serif;font-size:2.6px;fill:#17283b}.port{fill:#e1effa;stroke:#285a85;stroke-width:.25}.pin{fill:#285a85}.power{fill:#fde8ce;stroke:#98632f;stroke-width:.25}.note{font-size:2.5px;fill:#5b6874}.small{font-size:2.1px}</style>
<rect x="-10" y="-18" width="110" height="112" fill="white"/>
<rect x="0" y="0" width="90" height="70" rx="1" fill="#f8fafc" stroke="#17283b" stroke-width=".4"/>
<text x="0" y="-12" font-size="4">R0 BENCH CARRIER / OWN_DESIGN</text>
<text x="0" y="-7" class="note">90 × 70 mm • dimensions mm • no final back fit / no PCB CAD</text>
<text x="0" y="-3" class="note">Top view; local +X →, +Y ↑; connector envelopes ESTIMATED</text>
'@
foreach($hole in $model.board.mounting_holes) {
 $sy=70-$hole.y_mm
 $svg += "`n<circle cx='$($hole.x_mm)' cy='$sy' r='1.6' fill='white' stroke='#17283b' stroke-width='.3'/><text x='$($hole.x_mm+2)' y='$($sy+1)' class='small'>$($hole.id)</text>"
}
foreach($port in $ports) {
 $x=[double]$port.center_mm[0];$sy=70-[double]$port.center_mm[1]
 if($port.reference -eq 'J_USB') { $svg += "`n<rect x='39.5' y='63' width='11' height='8' class='power'/><text x='39' y='77'>J_USB → -Y</text>"; continue }
 $count=$port.pins.Count
 $w=if($port.reference -eq 'J_CTRL'){61.42}else{($count-1)*$port.pitch_mm+3}
 $h=if($port.reference -eq 'J_CTRL'){5.54}else{3}
 $class=if($port.reference -in @('J_MA','J_MB','J_VM','J_BAT')){'power'}else{'port'}
 $svg += "`n<rect x='$([Math]::Round($x-$w/2,2))' y='$([Math]::Round($sy-$h/2,2))' width='$w' height='$h' class='$class'/>"
 foreach($pin in $port.pins) {
  $py=70-$pin.y_mm
  if($pin.pin -eq 1) { $svg += "`n<rect x='$($pin.x_mm-.55)' y='$($py-.55)' width='1.1' height='1.1' class='pin'/>" }
  else { $svg += "`n<circle cx='$($pin.x_mm)' cy='$py' r='.45' class='pin'/>" }
 }
 $labelY=$sy-$h/2-1
 $svg += "`n<text x='$([Math]::Round($x-$w/2,2))' y='$labelY' class='small'>$($port.reference)</text>"
}
$svg += @'
<path d="M0 70 H7 M0 70 V63" fill="none" stroke="#ce5353" stroke-width=".5"/>
<text x="-7" y="74">(0,0)</text>
<text x="0" y="83" class="note">4 × Ø3.2 at (4,4), (86,4), (86,66), (4,66): own bench mounting only.</text>
<text x="0" y="87" class="note">Signal pin1 = square. Supplier footprint, current rating and MCU pad mapping pending.</text>
</svg>
'@
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'R0_bench-interface.svg'),$svg,$utf8NoBom)
Write-Output 'Generated own-design bench JSON/SVG; no installed mechanical fit or hardware validation.'
