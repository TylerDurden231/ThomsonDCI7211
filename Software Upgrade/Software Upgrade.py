# -*- coding: utf-8 -*-
# Test name = Software Upgrade
# Test description = Set environment, perform software upgrade and check STB state after sw upgrade

from datetime import datetime
from time import gmtime, strftime
import time
import device
import TEST_CREATION_API
import shutil
import os.path
import sys

try:    
    if ((os.path.exists(os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py")) == False) or (str(os.path.getmtime('\\\\rt-rk01\\RT-Executor\\API\\NOS_API.py')) != str(os.path.getmtime(os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py"))))):
        shutil.copy2('\\\\rt-rk01\\RT-Executor\\API\\NOS_API.py', os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py"))
except:
    pass
    
import NOS_API

try:
    # Get model
    model_type = NOS_API.get_model()

    # Check if folder with thresholds exists, if not create it
    if(os.path.exists(os.path.join(os.path.dirname(sys.executable), "Thresholds")) == False):
        os.makedirs(os.path.join(os.path.dirname(sys.executable), "Thresholds"))

    # Copy file with threshold if does not exists or if it is updated
    if ((os.path.exists(os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt")) == False) or (str(os.path.getmtime(NOS_API.THRESHOLDS_PATH + model_type + ".txt")) != str(os.path.getmtime(os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt"))))):
        shutil.copy2(NOS_API.THRESHOLDS_PATH + model_type + ".txt", os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt"))
except Exception as error_message:
    pass

## Number of alphanumeric characters in SN
SN_LENGTH = 15  

## Number of alphanumeric characters in Cas_Id
CASID_LENGTH = 12

## Number of alphanumeric characters in MAC
MAC_LENGTH = 12 

## Time in seconds which define when dialog will be closed
DIALOG_TIMEOUT = 10

## Constant multiplier used for conversion from seconds to milliseconds
MS_MULTIPLIER = 1000

## Max time to perform sw upgrade (in seconds)
SW_UPGRADE_TIMEOUT = 400

## Time needed to STB power on (in seconds)
WAIT_TO_POWER_STB = 20

## Time to press V+/V- simultaneous in seconds
TIMEOUT_CAUSE_SW_UPGRADE = 4

## Time to switch from HDMI to SCART in seconds
WAIT_TO_SWITCH_SCART = 6

NOS_API.grabber_type()
TEST_CREATION_API.grabber_type()

def runTest():
   
    NOS_API.read_thresholds()
    
    NOS_API.reset_test_cases_results_info() 
 
    ## Set test result default to FAIL
    test_result = "FAIL"
 
    error_codes = ""
    error_messages = ""
    SN_LABEL = False
    CASID_LABEL = False
    MAC_LABEL = False   
    
    ## Read STB Labels using barcode reader (S/N, CAS ID, MAC and SAP) and LOG it 
    try:      
        all_scanned_barcodes = NOS_API.get_all_scanned_barcodes()
        NOS_API.test_cases_results_info.s_n_using_barcode = all_scanned_barcodes[1]
        NOS_API.test_cases_results_info.cas_id_using_barcode = all_scanned_barcodes[2]
        NOS_API.test_cases_results_info.mac_using_barcode = all_scanned_barcodes[3]
        NOS_API.test_cases_results_info.nos_sap_number = all_scanned_barcodes[0]
    except Exception as error:
        TEST_CREATION_API.write_log_to_file(error)
        test_result = "FAIL"
        #TEST_CREATION_API.update_test_result(test_result)                
        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scan_error_code \
                                           + "; Error message: " + NOS_API.test_cases_results_info.scan_error_message)
        NOS_API.set_error_message("Leitura de Etiquetas")
        error_codes = NOS_API.test_cases_results_info.scan_error_code
        error_messages = NOS_API.test_cases_results_info.scan_error_message 
                  
    test_number = NOS_API.get_test_number(NOS_API.test_cases_results_info.s_n_using_barcode)
    device.updateUITestSlotInfo("Teste N\xb0: " + str(int(test_number)+1))
    
    if ((len(NOS_API.test_cases_results_info.s_n_using_barcode) == SN_LENGTH) and (NOS_API.test_cases_results_info.s_n_using_barcode.isalnum() or NOS_API.test_cases_results_info.s_n_using_barcode.isdigit()) and (NOS_API.test_cases_results_info.cas_id_using_barcode != NOS_API.test_cases_results_info.mac_using_barcode)):
        SN_LABEL = True

    if ((len(NOS_API.test_cases_results_info.cas_id_using_barcode) == CASID_LENGTH) and (NOS_API.test_cases_results_info.cas_id_using_barcode.isalnum() or NOS_API.test_cases_results_info.cas_id_using_barcode.isdigit())):
        CASID_LABEL = True

    if ((len(NOS_API.test_cases_results_info.mac_using_barcode) == MAC_LENGTH) and (NOS_API.test_cases_results_info.mac_using_barcode.isalnum() or NOS_API.test_cases_results_info.mac_using_barcode.isdigit())):
        MAC_LABEL = True
        
    if not(SN_LABEL and CASID_LABEL and MAC_LABEL):
        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scan_error_code \
                                       + "; Error message: " + NOS_API.test_cases_results_info.scan_error_message)
        NOS_API.set_error_message("Leitura de Etiquetas")
        error_codes = NOS_API.test_cases_results_info.scan_error_code
        error_messages = NOS_API.test_cases_results_info.scan_error_message
        test_result = "FAIL"
        
        NOS_API.add_test_case_result_to_file_report(
                        test_result,
                        "- - - - - - - - - - - - - - - - - - - -",
                        "- - - - - - - - - - - - - - - - - - - -",
                        error_codes,
                        error_messages)
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        report_file = ""
        if (test_result != "PASS"):
            report_file = NOS_API.create_test_case_log_file(
                            NOS_API.test_cases_results_info.s_n_using_barcode,
                            NOS_API.test_cases_results_info.nos_sap_number,
                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                            NOS_API.test_cases_results_info.mac_using_barcode,
                            end_time)
            NOS_API.upload_file_report(report_file)
            NOS_API.test_cases_results_info.isTestOK = False
        
        
        ## Update test result
        TEST_CREATION_API.update_test_result(test_result)
        
        ## Return DUT to initial state and de-initialize grabber device
        NOS_API.deinitialize()
        
        NOS_API.send_report_over_mqtt_test_plan(
            test_result,
            end_time,
            error_codes,
            report_file)
        
        return
      
    System_Failure = 0
    while (System_Failure < 2):
        try:
            test_result = "FAIL"
            result = False
            error_codes = ""
            error_messages = ""

            if (NOS_API.configure_power_switch_by_inspection()):
                NOS_API.power_off() 
                time.sleep(3)

            if ((len(NOS_API.test_cases_results_info.mac_using_barcode) == MAC_LENGTH) and (NOS_API.test_cases_results_info.mac_using_barcode.isalnum() or NOS_API.test_cases_results_info.mac_using_barcode.isdigit())):
                ## Power on STB with energenie
                if (NOS_API.configure_power_switch_by_inspection()):
                    NOS_API.power_on()
                if (System_Failure == 0):
                    if not(NOS_API.display_new_dialog("Conectores?", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                        TEST_CREATION_API.write_log_to_file("Conectores NOK")
                        NOS_API.set_error_message("Danos Externos")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.conector_nok_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.conector_nok_error_message)
                        error_codes = NOS_API.test_cases_results_info.conector_nok_error_code
                        error_messages = NOS_API.test_cases_results_info.conector_nok_error_message
                        test_result = "FAIL"
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                        
                        return
                    if not(NOS_API.display_new_dialog("Chassis?", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                        TEST_CREATION_API.write_log_to_file("Chassis NOK")
                        NOS_API.set_error_message("Danos Externos")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.chassis_nok_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.chassis_nok_error_message) 
                        error_codes = NOS_API.test_cases_results_info.chassis_nok_error_code
                        error_messages = NOS_API.test_cases_results_info.chassis_nok_error_message
                        test_result = "FAIL"
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                        
                        return            
                    if not(NOS_API.display_custom_dialog("A STB est\xe1 ligada?Insira o SmartCard", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                        TEST_CREATION_API.write_log_to_file("No Power")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_power_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.no_power_error_message) 
                        NOS_API.set_error_message("Não Liga") 
                        error_codes =  NOS_API.test_cases_results_info.no_power_error_code
                        error_messages = NOS_API.test_cases_results_info.no_power_error_message
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False

                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                        return             
                    if not(NOS_API.display_custom_dialog("Ventoinha?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                        TEST_CREATION_API.write_log_to_file("FAN is not running")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.fan_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.fan_error_message)
                        NOS_API.set_error_message("Ventoinha")
                        error_codes = NOS_API.test_cases_results_info.fan_error_code
                        error_messages = NOS_API.test_cases_results_info.fan_error_message
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False

                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                        return 
                    
                    time.sleep(3)
                    #if (NOS_API.display_custom_dialog("O display est\xe1 ligado?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                    time.sleep(5)
                    if (NOS_API.display_custom_dialog("A STB est\xe1 a atualizar?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                        NOS_API.wait_for_signal_present(500)
                        NOS_API.test_cases_results_info.DidUpgrade = 1
                
                NOS_API.grabber_hour_reboot()
                
                ## Initialize grabber device
                NOS_API.initialize_grabber()

                ## Start grabber device with video on default video source
                NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                
                ## Check is signal present on HDMI during sw upgrade 
                if (NOS_API.is_signal_present_on_video_source()):
                    
                    ## Wait to display image after signal is present 
                    time.sleep(5)
                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                        time.sleep(20)
                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                            NOS_API.set_error_message("Video HDMI")
                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False


                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                            
                            return 
                            
                    if not(NOS_API.grab_picture("screen")):
                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                        NOS_API.set_error_message("Reboot")
                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                        test_result = "FAIL"
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False


                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                        
                        return                                 
                    
                    if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                        TEST_CREATION_API.send_ir_rc_command("[CH+]")
                        time.sleep(2)
                        TEST_CREATION_API.send_ir_rc_command("[CH-]")
                        time.sleep(2)
                        TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                        time.sleep(1)
                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                        
                        if not(NOS_API.grab_picture("screen")):
                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                            NOS_API.set_error_message("Reboot")
                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False


                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                            
                            return 
                                                            
                        if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                            time.sleep(5)
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            time.sleep(10)
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            time.sleep(5)
                            TEST_CREATION_API.send_ir_rc_command("[CH+]")
                            time.sleep(2)
                            TEST_CREATION_API.send_ir_rc_command("[CH-]")
                            time.sleep(1)
                            TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                            time.sleep(1)
                            TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                                              
                                    
                    TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                    time.sleep(2)
                    TEST_CREATION_API.send_ir_rc_command("[EXIT_WITHOUT_DELAY]")
                    TEST_CREATION_API.send_ir_rc_command("[MENU]")
                    if not(NOS_API.grab_picture("menu")):                       
                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                        NOS_API.set_error_message("Reboot")
                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                        test_result = "FAIL"
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False


                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                        return        
                
                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                        time.sleep(20)
                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                            NOS_API.set_error_message("Video HDMI")
                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False


                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                            
                            return 
                                                    
                    if(video_height == "720"):
                        if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                            if (TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres)):
                                NOS_API.test_cases_results_info.isTestOK = False  
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                NOS_API.set_error_message("Não Actualiza")
                                error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                test_result = "FAIL"

                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                return 
                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                            time.sleep(300)
                            NOS_API.test_cases_results_info.DidUpgrade = 1
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            time.sleep(5)
                            if not(NOS_API.grab_picture("menu")):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                
                                return 
                                    
                            if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                if (TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres)):
                                    NOS_API.test_cases_results_info.isTestOK = False  
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                    NOS_API.set_error_message("Não Actualiza")
                                    error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                    test_result = "FAIL"

                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                    return
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                time.sleep(120)
                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                time.sleep(5)
                                if not(NOS_API.grab_picture("menu")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"    
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False

                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                            
                                if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                    NOS_API.test_cases_results_info.isTestOK = False  
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                    NOS_API.set_error_message("Não Actualiza")
                                    error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                    test_result = "FAIL"

                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                    return                                                
                        
                    if(video_height!= "720"):
                        NOS_API.SET_720 = True
                    else:
                        NOS_API.SET_720 = False
                    
                    if not(video_height == "576"):
                        threshold = NOS_API.thres
                        
                    else:
                        threshold = NOS_API.DEFAULT_CVBS_VIDEO_THRESHOLD
                        
                        
                    if not(TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold)):
                        TEST_CREATION_API.send_ir_rc_command("[MENU]")
                        if not(NOS_API.grab_picture("menu")):
                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                            NOS_API.set_error_message("Reboot")
                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False


                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                            return

                    ## Depends on resolution set appropriate picture and macro
                    if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold)):
                        if(NOS_API.SET_720):
                            ## Set resolution to 720p and navigate to the signal level settings
                            TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p_T7211]")
                            TEST_CREATION_API.send_ir_rc_command("[INIT]")
                            time.sleep(3)
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if(video_height != "720"):
                                time.sleep(1)
                                TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p_T7211]")
                                TEST_CREATION_API.send_ir_rc_command("[INIT]")
                                time.sleep(3)
                                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "720"):
                                    NOS_API.set_error_message("Resolução")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                    error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                    error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                    test_result = "FAIL"
                                
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                
                
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return 

                       #NOS_API.test_cases_results_info.channel_boot_up_state = True
                        ##############################################
                        #if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold)):
                        #    NOS_API.IN_PT = False
                        ########
                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                        time.sleep(5)
                        if (NOS_API.is_signal_present_on_video_source()):
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            time.sleep(5)
                        if (NOS_API.is_signal_present_on_video_source()):
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                            NOS_API.set_error_message("IR")
                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                            TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False


                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                            
                            return
                        TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                        time.sleep(5)
                        if (NOS_API.is_signal_present_on_video_source()):
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                time.sleep(20)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                            if not(NOS_API.grab_picture("Inst_Mode")):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                
                                return
                            if(video_height == "720"):
                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                            elif(video_height == "1080"):
                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                            if (result or result_1):
                                NOS_API.test_cases_results_info.channel_boot_up_state = False
                            else:
                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                    NOS_API.set_error_message("IR")
                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                        time.sleep(20)
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                    if not(NOS_API.grab_picture("Inst_Mode")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    if(video_height == "720"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                    elif(video_height == "1080"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                    if (result or result_1):
                                        NOS_API.test_cases_results_info.channel_boot_up_state = False
                                    else:
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                        NOS_API.set_error_message("IR")
                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                        TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                else:
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                    NOS_API.set_error_message("IR")
                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                        else:            
                            TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                            time.sleep(5) 
                            if (NOS_API.is_signal_present_on_video_source()):
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    time.sleep(20)
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                        TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                if not(NOS_API.grab_picture("Inst_Mode")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
    
    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                if(video_height == "720"):
                                    result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                    result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                elif(video_height == "1080"):
                                    result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                    result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                if (result or result_1):
                                    NOS_API.test_cases_results_info.channel_boot_up_state = False
                                else:
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(5)
                                    if (NOS_API.is_signal_present_on_video_source()):
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                    if (NOS_API.is_signal_present_on_video_source()):
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                        NOS_API.set_error_message("IR")
                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                        TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    if not(TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")):
                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    time.sleep(5)
                                    if (NOS_API.is_signal_present_on_video_source()):
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            time.sleep(20)
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                        if not(NOS_API.grab_picture("Inst_Mode")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        if(video_height == "720"):
                                            result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                        elif(video_height == "1080"):
                                            result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                            result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                        if (result or result_1):
                                            NOS_API.test_cases_results_info.channel_boot_up_state = False
                                        else:
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                    else:
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                        NOS_API.set_error_message("IR")
                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                        TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                            else:
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                NOS_API.set_error_message("IR")
                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                
                                return
                        ##PUT HERE THE COMMAND 2008POWER###
                        ##NOS_API.test_cases_results_info.channel_boot_up_state = False
                        
                        #####
                        ##############################################
                    else:
                        if (video_height != "720"):
                            #Nao ha casos para 576
                            if (video_height == "1080"):
                                if (TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "menu", "[Inst_Mode_1080]", NOS_API.thres)):
                                    TEST_CREATION_API.write_log_to_file("Installation Resolution")
                                    NOS_API.test_cases_results_info.isTestOK = False
                                    NOS_API.set_error_message("Resolução")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                    error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                    error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                    test_result = "FAIL"
                                
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                
                
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return 
                                else:
                                    TEST_CREATION_API.write_log_to_file("Video HDMI")
                                    NOS_API.test_cases_results_info.isTestOK = False
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message                                        
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                    
                                    return
                            
                            else:
                                TEST_CREATION_API.write_log_to_file("Video HDMI")
                                NOS_API.test_cases_results_info.isTestOK = False
                                NOS_API.set_error_message("Video HDMI")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message                                        
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                
                                return  
                        
                        if not(NOS_API.grab_picture("Status_Check")):
                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                            NOS_API.set_error_message("Reboot")
                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False


                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                            
                            return
                        if(TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Status_Check", "[Inst_Mode]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("installation_boot_up_ref2", "Status_Check", "[Inst_Mode]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("installation_boot_up_ref3", "Status_Check", "[Inst_Mode]", NOS_API.thres)):
                            NOS_API.test_cases_results_info.channel_boot_up_state = False
                        else:
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            TEST_CREATION_API.send_ir_rc_command("[MENU]")
                            TEST_CREATION_API.send_ir_rc_command("[MENU]")
                            time.sleep(1)
                            if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", NOS_API.thres)):
                                TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                time.sleep(5) 
                                if (NOS_API.is_signal_present_on_video_source()):
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                        time.sleep(20)
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                    if not(NOS_API.grab_picture("Inst_Mode")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    if(video_height == "720"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                    elif(video_height == "1080"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                    if (result or result_1):
                                        NOS_API.test_cases_results_info.channel_boot_up_state = False
                                    else:
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                            time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        if not(TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")):
                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                time.sleep(20)
                                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                            if not(NOS_API.grab_picture("Inst_Mode")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            if(video_height == "720"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            elif(video_height == "1080"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                            if (result or result_1):
                                                NOS_API.test_cases_results_info.channel_boot_up_state = False
                                            else:
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                NOS_API.set_error_message("IR")
                                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                        else:
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                else:
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                    NOS_API.set_error_message("IR")
                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                            ##PUT HERE THE COMMAND 2008POWER###
                            ##NOS_API.test_cases_results_info.channel_boot_up_state = False
                            
                            #####
                            ##############################################
                            else:
                                TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_message)
                                error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                                error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message
                                        
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = ""    
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.set_error_message("Video HDMI") 
                                    NOS_API.test_cases_results_info.isTestOK = False
                            
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                            
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                    
                                return

                    test_result = "PASS"
                else:
                    NOS_API.grabber_stop_video_source()
                    time.sleep(1)
                    
                    ## Initialize input interfaces of DUT RT-AV101 device 
                    NOS_API.reset_dut()
                    #time.sleep(2)
                    
                    ## Start grabber device with video on SCART video source
                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                    time.sleep(WAIT_TO_SWITCH_SCART)
                    ## Check is signal present on SCART
                    if (NOS_API.is_signal_present_on_video_source()):
                        
                        if not(NOS_API.grab_picture("SCART_IMAGE")):
                            TEST_CREATION_API.write_log_to_file("Couldn't capture SCART Image")                                          
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message)
                            NOS_API.set_error_message("Video SCART")
                            error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                            error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False


                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                            return
                            
                        NOS_API.grabber_stop_video_source()
                        time.sleep(1)
                        ## Start grabber device with video on HDMI video source
                        NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                        time.sleep(3)
                        if not(NOS_API.is_signal_present_on_video_source()):
                            NOS_API.display_dialog("Confirme o cabo HDMI e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                            time.sleep(3)
                            if not(NOS_API.is_signal_present_on_video_source()):
                                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                NOS_API.set_error_message("Video HDMI (Não Restestar)")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                return
                        ## If signal is not present on HDMI, power on STB
                        if not(NOS_API.is_signal_present_on_video_source()):
                            ## Press POWER key
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            if not(NOS_API.is_signal_present_on_video_source()):
                                time.sleep(3)
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                time.sleep(20)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                            if not(NOS_API.grab_picture("menu")):                                        
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                return
                            #if(TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]") or TEST_CREATION_API.compare_pictures("update_screen_720_ref2", "menu", "[UPDATE_SCREEN]")):
                            if(TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):    
                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                #time.sleep(340)
                                NOS_API.test_cases_results_info.DidUpgrade = 1
                                NOS_API.wait_for_signal_present(400)
                                time.sleep(5)
                                if not(NOS_API.is_signal_present_on_video_source()):
                                    time.sleep(5)
                                if not(NOS_API.is_signal_present_on_video_source()):
                                    time.sleep(3)
                                if not(NOS_API.is_signal_present_on_video_source()):
                                    time.sleep(3)
                                if not(NOS_API.grab_picture("menu")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    return

                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                time.sleep(20)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                            if not(NOS_API.grab_picture("screen")):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                return                                 
                            
                            if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                time.sleep(2)
                                TEST_CREATION_API.send_ir_rc_command("[CH-]")                                        
                                time.sleep(2)
                                TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                time.sleep(1)
                                TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                
                                if not(NOS_API.grab_picture("screen")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    return
                                    
                            
                                if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                    time.sleep(5)
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(15)
                                    if not(NOS_API.is_signal_present_on_video_source()):
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                    TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                    time.sleep(2)
                                    TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                    time.sleep(1)
                                    TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                    time.sleep(1)
                                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                
                            TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                            time.sleep(2)
                            ## check is signal present after STB is powered on
                        if (NOS_API.is_signal_present_on_video_source()):
                            
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            TEST_CREATION_API.send_ir_rc_command("[MENU]")
                            TEST_CREATION_API.send_ir_rc_command("[MENU]")
                            if not(NOS_API.is_signal_present_on_video_source()):
                                time.sleep(3)
                            if not(NOS_API.grab_picture("menu")):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                return
                            
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                time.sleep(20)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                            if(video_height == "720"):
                                if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                    if (TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres)):
                                        NOS_API.test_cases_results_info.isTestOK = False  
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                        + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                        NOS_API.set_error_message("Não Actualiza")
                                        error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                        test_result = "FAIL"
    
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                        return
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                    time.sleep(300)
                                    NOS_API.test_cases_results_info.DidUpgrade = 1
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(5)
                                    if not(NOS_API.grab_picture("menu")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    
                                    if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                        if (TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres)):
                                            NOS_API.test_cases_results_info.isTestOK = False  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                            + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                            NOS_API.set_error_message("Não Actualiza")
                                            error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                            test_result = "FAIL"
        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                            return
                                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                                        time.sleep(120)
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                        if not(NOS_API.grab_picture("menu")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            return
                                            
                                        if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                            NOS_API.test_cases_results_info.isTestOK = False  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                            + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                            NOS_API.set_error_message("Não Actualiza")
                                            error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                            test_result = "FAIL"
        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                            return                                                
                            
                                
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                time.sleep(20)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                            if(video_height!= "720"):
                                NOS_API.SET_720 = True
                            else:
                                NOS_API.SET_720 = False
                    
                            
                            if not(video_height == "576"):
                                threshold = NOS_API.thres
                                
                            else:
                                threshold = NOS_API.DEFAULT_CVBS_VIDEO_THRESHOLD
                            
                            ## Depends on resolution set appropriate picture and macro
                            if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold)):
                                #NOS_API.test_cases_results_info.channel_boot_up_state = True
                                ########
                                
                                if(NOS_API.SET_720):
                                    ## Set resolution to 720p and navigate to the signal level settings
                                    TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p_T7211]")
                                    TEST_CREATION_API.send_ir_rc_command("[INIT]")
                                    time.sleep(3)
                                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if(video_height != "720"):
                                        time.sleep(1)
                                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                        TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p_T7211]")
                                        TEST_CREATION_API.send_ir_rc_command("[INIT]")
                                        time.sleep(3)
                                        TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "720"):
                                            NOS_API.set_error_message("Resolução")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                            error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                            error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                            test_result = "FAIL"
                                        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return 
    
                                
                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                    NOS_API.set_error_message("IR")
                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                        time.sleep(20)
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                    if not(NOS_API.grab_picture("Inst_Mode")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    if(video_height == "720"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                    elif(video_height == "1080"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                    if (result or result_1):
                                        NOS_API.test_cases_results_info.channel_boot_up_state = False
                                    else:
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                            time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                        time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                time.sleep(20)
                                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                            if not(NOS_API.grab_picture("Inst_Mode")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            
                                            if(video_height == "720"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            elif(video_height == "1080"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                            if (result or result_1):
                                                NOS_API.test_cases_results_info.channel_boot_up_state = False
                                            else:
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                NOS_API.set_error_message("IR")
                                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                        else:
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                else:            
                                    TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                    time.sleep(5) 
                                    if (NOS_API.is_signal_present_on_video_source()):
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            time.sleep(20)
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                        if not(NOS_API.grab_picture("Inst_Mode")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        if(video_height == "720"):
                                            result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                        elif(video_height == "1080"):
                                            result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thresD)
                                            result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                        if (result or result_1):
                                            NOS_API.test_cases_results_info.channel_boot_up_state = False
                                        else:
                                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                            time.sleep(5)
                                            if (NOS_API.is_signal_present_on_video_source()):
                                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                time.sleep(5)
                                            if (NOS_API.is_signal_present_on_video_source()):
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                NOS_API.set_error_message("IR")
                                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                            time.sleep(5)
                                            if (NOS_API.is_signal_present_on_video_source()):
                                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                    time.sleep(20)
                                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                        TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                        NOS_API.set_error_message("Video HDMI")
                                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                        
                                                        return
                                                if not(NOS_API.grab_picture("Inst_Mode")):
                                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                    NOS_API.set_error_message("Reboot")
                                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                                if(video_height == "720"):
                                                    result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                    result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                elif(video_height == "1080"):
                                                    result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                    result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                if (result or result_1):
                                                    NOS_API.test_cases_results_info.channel_boot_up_state = False
                                                else:
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                            else:
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                NOS_API.set_error_message("IR")
                                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                    else:
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                        NOS_API.set_error_message("IR")
                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                        TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                ##PUT HERE THE COMMAND 2008POWER###
                                ##NOS_API.test_cases_results_info.channel_boot_up_state = False
                                
                                #####
                                ##############################################
                                #if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold)):
                                #    NOS_API.IN_PT = False
                                
                                ##############################################
                            else:
                                if (video_height != "720"):
                        
                                    if (video_height == "1080"):
                                        if (TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "menu", "[Inst_Mode_1080]", NOS_API.thres)):
                                            TEST_CREATION_API.write_log_to_file("Installation Resolution")
                                            NOS_API.test_cases_results_info.isTestOK = False
                                            NOS_API.set_error_message("Resolução")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                            error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                            error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                            test_result = "FAIL"
                                        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return 
                                        else:
                                            TEST_CREATION_API.write_log_to_file("Video HDMI")
                                            NOS_API.test_cases_results_info.isTestOK = False
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message                                        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                            
                                            return 
                                    if (video_height == "576"):                                       
                                        TEST_CREATION_API.write_log_to_file("Video HDMI")
                                        NOS_API.test_cases_results_info.isTestOK = False
                                        NOS_API.set_error_message("Video HDMI")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                        
                                        return 
                                    
                                if not(NOS_API.grab_picture("Status_Check")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
    
    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                if(TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Status_Check", "[Inst_Mode]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("installation_boot_up_ref2", "Status_Check", "[Inst_Mode]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("installation_boot_up_ref3", "Status_Check", "[Inst_Mode]", NOS_API.thres)):
                                    NOS_API.test_cases_results_info.channel_boot_up_state = False
                                else:
                                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                    TEST_CREATION_API.send_ir_rc_command("[MENU]")
                                    TEST_CREATION_API.send_ir_rc_command("[MENU]")
                                    time.sleep(1)
                                    if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", threshold)):
                                        TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                        time.sleep(5) 
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                time.sleep(20)
                                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                            if not(NOS_API.grab_picture("Inst_Mode")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            if(video_height == "720"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            elif(video_height == "1080"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                            if (result or result_1):
                                                NOS_API.test_cases_results_info.channel_boot_up_state = False
                                            else:
                                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                time.sleep(5)
                                                if (NOS_API.is_signal_present_on_video_source()):
                                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                    time.sleep(5)
                                                if (NOS_API.is_signal_present_on_video_source()):
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                                if not(TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")):
                                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                                time.sleep(5)
                                                if (NOS_API.is_signal_present_on_video_source()):
                                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                        time.sleep(20)
                                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                            NOS_API.set_error_message("Video HDMI")
                                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                            test_result = "FAIL"
                                                            
                                                            NOS_API.add_test_case_result_to_file_report(
                                                                            test_result,
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            error_codes,
                                                                            error_messages)
                                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                            report_file = ""
                                                            if (test_result != "PASS"):
                                                                report_file = NOS_API.create_test_case_log_file(
                                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                                end_time)
                                                                NOS_API.upload_file_report(report_file)
                                                                NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                                            ## Update test result
                                                            TEST_CREATION_API.update_test_result(test_result)
                                                            
                                                            ## Return DUT to initial state and de-initialize grabber device
                                                            NOS_API.deinitialize()
                                                            
                                                            NOS_API.send_report_over_mqtt_test_plan(
                                                                test_result,
                                                                end_time,
                                                                error_codes,
                                                                report_file)
                                                            
                                                            return
                                                    if not(NOS_API.grab_picture("Inst_Mode")):
                                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                        NOS_API.set_error_message("Reboot")
                                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                        
                                                        return
                                                    if(video_height == "720"):
                                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                    elif(video_height == "1080"):
                                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                    if (result or result_1):
                                                        NOS_API.test_cases_results_info.channel_boot_up_state = False
                                                    else:
                                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                        NOS_API.set_error_message("IR")
                                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                        TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                        
                                                        return
                                                else:
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                        else:
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False


                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                    ##PUT HERE THE COMMAND 2008POWER###
                                    ##NOS_API.test_cases_results_info.channel_boot_up_state = False
                                    
                                    #####
                                    ##############################################
                                    else:
                                        TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_message)
                                        error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                                        error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message
                                                
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        report_file = ""    
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.set_error_message("Video HDMI") 
                                            NOS_API.test_cases_results_info.isTestOK = False
                                    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                    
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                            
                                        return
                            test_result = "PASS"
                        else:
                            NOS_API.grabber_stop_video_source()
                            time.sleep(1)
                            
                            ## Initialize input interfaces of DUT RT-AV101 device 
                            NOS_API.reset_dut()
                            #time.sleep(2)
                            
                            ## Start grabber device with video on SCART video source
                            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                            time.sleep(WAIT_TO_SWITCH_SCART)

                            ## Check is signal present on SCART
                            if (NOS_API.is_signal_present_on_video_source()):
                                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                NOS_API.set_error_message("Video HDMI")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                            else:
                                TEST_CREATION_API.write_log_to_file("No boot")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                                NOS_API.set_error_message("Não arranca")
                                error_codes = NOS_API.test_cases_results_info.no_boot_error_code
                                error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                            
                    else:
                        NOS_API.grabber_stop_video_source()
                        time.sleep(1)
                        ## Start grabber device with video on HDMI video source
                        NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                        time.sleep(3)
                        
                        ## If signal is not present on HDMI, power on STB
                        if not(NOS_API.is_signal_present_on_video_source()):
                            ## Press POWER key
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            if not(NOS_API.is_signal_present_on_video_source()):
                                time.sleep(3)
                                #if not(NOS_API.is_signal_present_on_video_source()):
                                #    NOS_API.display_dialog("Confirme o cabo HDMI e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                            if not(NOS_API.wait_for_signal_present(30)):
                                NOS_API.grabber_stop_video_source()
                                time.sleep(1)
                            
                                ## Initialize input interfaces of DUT RT-AV101 device 
                                NOS_API.reset_dut()
                                #time.sleep(2)
                                
                                ## Start grabber device with video on SCART video source
                                NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                                time.sleep(WAIT_TO_SWITCH_SCART)

                                ## Check is signal present on SCART
                                if (NOS_API.is_signal_present_on_video_source()):
                                                                        
                                    if not(NOS_API.grab_picture("SCART_IMAGE")):
                                        TEST_CREATION_API.write_log_to_file("Couldn't capture SCART Image")                                          
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message)
                                        NOS_API.set_error_message("Video SCART")
                                        error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                                        error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        return                                                                
            
                                    
                                    NOS_API.display_dialog("Confirme o cabo HDMI e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                                    NOS_API.grabber_stop_video_source()
                                    time.sleep(1)
                                    ## Start grabber device with video on HDMI video source
                                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                    time.sleep(3)
                                    if not(NOS_API.is_signal_present_on_video_source()):
                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI (Não Retestar)")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        return
                                                            
                                else:
                                
                                    NOS_API.grabber_stop_video_source()
                                    time.sleep(1)
                                    ## Start grabber device with video on HDMI video source
                                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                    time.sleep(3)
                                
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    if not(NOS_API.is_signal_present_on_video_source()):
                                        time.sleep(3)
                            if not(NOS_API.wait_for_signal_present(30)):
                                
                                NOS_API.grabber_stop_video_source()
                                time.sleep(1)
                            
                                ## Initialize input interfaces of DUT RT-AV101 device 
                                NOS_API.reset_dut()
                                #time.sleep(2)
                                
                                ## Start grabber device with video on SCART video source
                                NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                                time.sleep(WAIT_TO_SWITCH_SCART)

                                ## Check is signal present on SCART
                                if (NOS_API.is_signal_present_on_video_source()):
                                                                        
                                    if not(NOS_API.grab_picture("SCART_IMAGE")):
                                        TEST_CREATION_API.write_log_to_file("Couldn't capture SCART Image")                                          
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message)
                                        NOS_API.set_error_message("Video SCART")
                                        error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                                        error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        return                                                                
            
                                    
                                    NOS_API.display_dialog("Confirme o cabo HDMI e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                                    NOS_API.grabber_stop_video_source()
                                    time.sleep(1)
                                    ## Start grabber device with video on HDMI video source
                                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                    time.sleep(3)
                                    if not(NOS_API.is_signal_present_on_video_source()):
                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI (Não retestar)")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        return
                            
                           
                                else:
                                
                                    NOS_API.grabber_stop_video_source()
                                    time.sleep(1)
                                    ## Start grabber device with video on HDMI video source
                                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                    time.sleep(3)
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                if not(NOS_API.is_signal_present_on_video_source()):
                                    time.sleep(3)
                            if(NOS_API.wait_for_signal_present(30)): 
                                time.sleep(2)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    time.sleep(20)
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                        TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                if not(NOS_API.grab_picture("menu")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                
                                if(video_height != "1080"):
                                    if(TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):    
                                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                                        NOS_API.wait_for_signal_present(400)
                                        NOS_API.test_cases_results_info.DidUpgrade = 1
                                        time.sleep(5)
                                        if not(NOS_API.is_signal_present_on_video_source()):
                                            time.sleep(5)
                                        if not(NOS_API.is_signal_present_on_video_source()):
                                            time.sleep(3)
                                        if not(NOS_API.is_signal_present_on_video_source()):
                                            time.sleep(3)
                                        if not(NOS_API.grab_picture("menu")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            return
                                            
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    time.sleep(20)
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                        TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return                                    
                                if not(NOS_API.grab_picture("screen")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    return
                                if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                    TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                    time.sleep(2)
                                    TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                    time.sleep(2)
                                    TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                    time.sleep(2)
                                    if not(NOS_API.grab_picture("screen")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                        TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                        time.sleep(2)
                                        TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                        time.sleep(2)
                                    TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                    time.sleep(1)
                                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                    time.sleep(2)
                                    if not(NOS_API.grab_picture("screen")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        return
                                    if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                        time.sleep(5)
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(10)
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                        TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                        time.sleep(2)
                                        TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                        time.sleep(1)
                                        TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                        time.sleep(1)
                                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                            else:
                                
                                NOS_API.grabber_stop_video_source()
                                time.sleep(1)
                            
                                ## Initialize input interfaces of DUT RT-AV101 device 
                                NOS_API.reset_dut()
                                #time.sleep(2)
                                
                                ## Start grabber device with video on SCART video source
                                NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                                time.sleep(WAIT_TO_SWITCH_SCART)

                                ## Check is signal present on SCART
                                if (NOS_API.is_signal_present_on_video_source()):
                                                                        
                                    if not(NOS_API.grab_picture("SCART_IMAGE")):
                                        TEST_CREATION_API.write_log_to_file("Couldn't capture SCART Image")                                          
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message)
                                        NOS_API.set_error_message("Video SCART")
                                        error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                                        error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        return                                                                
            
################################################################################################################################################################################################################


                                    NOS_API.display_dialog("Confirme o cabo HDMI e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                                    NOS_API.grabber_stop_video_source()
                                    time.sleep(1)
                                    ## Start grabber device with video on HDMI video source
                                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                    time.sleep(3)
                                    if(NOS_API.is_signal_present_on_video_source()):
                                        time.sleep(2)
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            time.sleep(20)
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                        if not(NOS_API.grab_picture("menu")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        
                                        if(TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):    
                                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                                            NOS_API.wait_for_signal_present(400)
                                            NOS_API.test_cases_results_info.DidUpgrade = 1
                                            time.sleep(5)
                                            if not(NOS_API.is_signal_present_on_video_source()):
                                                time.sleep(5)
                                            if not(NOS_API.is_signal_present_on_video_source()):
                                                time.sleep(3)
                                            if not(NOS_API.is_signal_present_on_video_source()):
                                                time.sleep(3)
                                            if not(NOS_API.grab_picture("menu")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                return
                                                    
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            time.sleep(20)
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return                                    
                                        if not(NOS_API.grab_picture("screen")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            return
                                        if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                            TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                            time.sleep(2)
                                            TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                            time.sleep(2)
                                            TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                            time.sleep(2)
                                            if not(NOS_API.grab_picture("screen")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                                TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                                time.sleep(2)
                                                TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                                time.sleep(2)
                                            TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                            time.sleep(1)
                                            TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                            time.sleep(2)
                                            if not(NOS_API.grab_picture("screen")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                return
                                            if(TEST_CREATION_API.compare_pictures("black_screen_" + video_height + "_ref", "screen")):
                                                time.sleep(5)
                                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                time.sleep(10)
                                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                time.sleep(5)
                                                TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                                time.sleep(2)
                                                TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                                time.sleep(1)
                                                TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                                                time.sleep(1)
                                                TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                            
    
                                    else:            
################################################################################################################################################################################################################
                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI (Não Retestar)")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        return
                                
                                else:
                                    TEST_CREATION_API.write_log_to_file("No boot")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                                    NOS_API.set_error_message("Não arranca")
                                    error_codes = NOS_API.test_cases_results_info.no_boot_error_code
                                    error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                
                    
                                
                        if (NOS_API.wait_for_signal_present(20)):
                            
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            TEST_CREATION_API.send_ir_rc_command("[MENU]")
                            TEST_CREATION_API.send_ir_rc_command("[MENU]")
                            time.sleep(1)
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            
                            if not(NOS_API.is_signal_present_on_video_source()):
                                time.sleep(3)
                            if not(NOS_API.grab_picture("menu")):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False


                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                
                                return
                            
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                time.sleep(20)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                            if(video_height == "720"):
                                if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                    if (TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres)):
                                        NOS_API.test_cases_results_info.isTestOK = False  
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                        + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                        NOS_API.set_error_message("Não Actualiza")
                                        error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                        test_result = "FAIL"
    
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                        return
                                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                                    time.sleep(300)
                                    NOS_API.test_cases_results_info.DidUpgrade = 1
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(5)
                                    if not(NOS_API.grab_picture("menu")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    
                                    if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                        if (TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres)):
                                            NOS_API.test_cases_results_info.isTestOK = False  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                            + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                            NOS_API.set_error_message("Não Actualiza")
                                            error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                            test_result = "FAIL"
        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                            return
                                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                                        time.sleep(120)
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                        if not(NOS_API.grab_picture("menu")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                            
                                        if(TEST_CREATION_API.compare_pictures("Old_Sw_Channel_2_ref", "menu", "[Old_Sw_Channel_2]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_2_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("Old_Sw_Channel_ref", "menu", "[Old_Sw_Channel]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("No_Upgrade_Error_ref", "menu", "[No_Upgrade_Error_720]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref3", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("blue_ref4", "menu", "[OLD_ZON]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_ref2", "menu", "[FULL_SCREEN]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]", NOS_API.thres)):
                                            NOS_API.test_cases_results_info.isTestOK = False  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_code \
                                                                                            + "; Error message: " + NOS_API.test_cases_results_info.sw_upgrade_nok_error_message)
                                            NOS_API.set_error_message("Não Actualiza")
                                            error_codes = NOS_API.test_cases_results_info.sw_upgrade_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.sw_upgrade_nok_error_message
                                            test_result = "FAIL"
        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                            
                                            return                                                
                        
                            if(video_height!= "720"):
                                NOS_API.SET_720 = True
                            else:
                                NOS_API.SET_720 = False
                    
                            if not(video_height == "576"):
                                threshold = NOS_API.thres
                            else:
                                threshold = NOS_API.DEFAULT_CVBS_VIDEO_THRESHOLD
                            
                            ## Depends on resolution set appropriate picture and macro
                            if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_ref", "menu", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold)):
                                #NOS_API.test_cases_results_info.channel_boot_up_state = True
                                ########
                                
                                if(NOS_API.SET_720):
                                    ## Set resolution to 720p and navigate to the signal level settings
                                    TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p_T7211]")
                                    TEST_CREATION_API.send_ir_rc_command("[INIT]")
                                    time.sleep(3)
                                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if(video_height != "720"):
                                        time.sleep(1)
                                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                        TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p_T7211]")
                                        TEST_CREATION_API.send_ir_rc_command("[INIT]")
                                        time.sleep(3)
                                        TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "720"):
                                            NOS_API.set_error_message("Resolução")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                            error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                            error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                            test_result = "FAIL"
                                        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return 
            
                                
                                
                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                    NOS_API.set_error_message("IR")
                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False


                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                        time.sleep(20)
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
        
        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                    if not(NOS_API.grab_picture("Inst_Mode")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    if(video_height == "720"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                    elif(video_height == "1080"):
                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                    if (result or result_1):
                                        NOS_API.test_cases_results_info.channel_boot_up_state = False
                                    else:
                                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                        time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                            time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                        time.sleep(5)
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                time.sleep(20)
                                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                            if not(NOS_API.grab_picture("Inst_Mode")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            if(video_height == "720"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            elif(video_height == "1080"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                            if (result or result_1):
                                                NOS_API.test_cases_results_info.channel_boot_up_state = False
                                            else:
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                NOS_API.set_error_message("IR")
                                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                        else:
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                else:            
                                    TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                    time.sleep(5) 
                                    if (NOS_API.is_signal_present_on_video_source()):
                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                            time.sleep(20)
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
            
            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                        if not(NOS_API.grab_picture("Inst_Mode")):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                        if(video_height == "720"):
                                            result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                        elif(video_height == "1080"):
                                            result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                            result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                        if (result or result_1):
                                            NOS_API.test_cases_results_info.channel_boot_up_state = False
                                        else:
                                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                            time.sleep(5)
                                            if (NOS_API.is_signal_present_on_video_source()):
                                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                time.sleep(5)
                                            if (NOS_API.is_signal_present_on_video_source()):
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                NOS_API.set_error_message("IR")
                                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                            time.sleep(5)
                                            if (NOS_API.is_signal_present_on_video_source()):
                                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                    time.sleep(20)
                                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                        TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                        NOS_API.set_error_message("Video HDMI")
                                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                        
                                                        return
                                                if not(NOS_API.grab_picture("Inst_Mode")):
                                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                    NOS_API.set_error_message("Reboot")
                                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                                if(video_height == "720"):
                                                    result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                    result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                elif(video_height == "1080"):
                                                    result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                    result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                if (result or result_1):
                                                    NOS_API.test_cases_results_info.channel_boot_up_state = False
                                                else:
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                            else:
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                NOS_API.set_error_message("IR")
                                                error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                    else:
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                        NOS_API.set_error_message("IR")
                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                        TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
    
    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                ##PUT HERE THE COMMAND 2008POWER###
                                ##NOS_API.test_cases_results_info.channel_boot_up_state = False
                                
                                #####
                               # ##############################################
                               # if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "menu", "[MENU_" + video_height + "]", threshold)):
                               #     NOS_API.IN_PT = False
                               # 
                                ##############################################
                            else:                                
                                if (video_height != "720"):
                        
                                    if (video_height == "1080"):
                                        if (TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "menu", "[Inst_Mode_1080]", NOS_API.thres)):
                                            TEST_CREATION_API.write_log_to_file("Installation Resolution")
                                            NOS_API.test_cases_results_info.isTestOK = False
                                            NOS_API.set_error_message("Resolução")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                            error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                            error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                            test_result = "FAIL"
                                        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return 
                                        else:
                                            TEST_CREATION_API.write_log_to_file("Noise Video HDMI")
                                            NOS_API.test_cases_results_info.isTestOK = False
                                            NOS_API.set_error_message("Video HDMI")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message) 
                                            error_codes = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_code
                                            error_messages = NOS_API.test_cases_results_info.hdmi_1080p_noise_error_message                                        
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                            
                                            return  
                                
                                if not(NOS_API.grab_picture("Status_Check")):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
    
    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                    
                                    return
                                if(TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Status_Check", "[Inst_Mode]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("installation_boot_up_ref2", "Status_Check", "[Inst_Mode]", NOS_API.thres) or TEST_CREATION_API.compare_pictures("installation_boot_up_ref3", "Status_Check", "[Inst_Mode]", NOS_API.thres)):
                                    NOS_API.test_cases_results_info.channel_boot_up_state = False
                                else:
                                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                    TEST_CREATION_API.send_ir_rc_command("[MENU]")
                                    TEST_CREATION_API.send_ir_rc_command("[MENU]")
                                    time.sleep(1)
                                    if not(NOS_API.grab_picture("Status_Check")):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
        
        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                        
                                        return
                                    if (TEST_CREATION_API.compare_pictures("menu_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("menu_cable_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_ref", "Status_Check", "[MENU_" + video_height + "]", threshold) or TEST_CREATION_API.compare_pictures("Menu_Black_" + video_height + "_eng_ref", "Status_Check", "[MENU_" + video_height + "]", threshold)):
                                        TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")
                                        time.sleep(5) 
                                        if (NOS_API.is_signal_present_on_video_source()):
                                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                            if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                time.sleep(20)
                                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                    TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                            if not(NOS_API.grab_picture("Inst_Mode")):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                
                                                return
                                            if(video_height == "720"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                            elif(video_height == "1080"):
                                                result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                            if (result or result_1):
                                                NOS_API.test_cases_results_info.channel_boot_up_state = False
                                            else:
                                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                time.sleep(5)
                                                if (NOS_API.is_signal_present_on_video_source()):
                                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                    time.sleep(5)
                                                if (NOS_API.is_signal_present_on_video_source()):
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power OFF")                        
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                                if not(TEST_CREATION_API.send_ir_rc_command("[Inst_Mode]")):
                                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                                time.sleep(5)
                                                if (NOS_API.is_signal_present_on_video_source()):
                                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                    if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                        time.sleep(20)
                                                        video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                                        if (video_height != "576" and video_height != "720" and video_height != "1080"):
                                                            TEST_CREATION_API.write_log_to_file("Detected height of HDMI Signal was " + video_height + ". Expected height was 576 or 720 or 1080.")
                                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                            NOS_API.set_error_message("Video HDMI")
                                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                            test_result = "FAIL"
                                                            
                                                            NOS_API.add_test_case_result_to_file_report(
                                                                            test_result,
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            error_codes,
                                                                            error_messages)
                                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                            report_file = ""
                                                            if (test_result != "PASS"):
                                                                report_file = NOS_API.create_test_case_log_file(
                                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                                end_time)
                                                                NOS_API.upload_file_report(report_file)
                                                                NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                                            ## Update test result
                                                            TEST_CREATION_API.update_test_result(test_result)
                                                            
                                                            ## Return DUT to initial state and de-initialize grabber device
                                                            NOS_API.deinitialize()
                                                            
                                                            NOS_API.send_report_over_mqtt_test_plan(
                                                                test_result,
                                                                end_time,
                                                                error_codes,
                                                                report_file)
                                                            
                                                            return
                                                    if not(NOS_API.grab_picture("Inst_Mode")):
                                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                        NOS_API.set_error_message("Reboot")
                                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                        
                                                        return
                                                    if(video_height == "720"):
                                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_eng_ref", "Inst_Mode", "[Inst_Mode]", NOS_API.thres)
                                                    elif(video_height == "1080"):
                                                        result = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                        result_1 = TEST_CREATION_API.compare_pictures("installation_boot_up_1080_eng_ref", "Inst_Mode", "[Inst_Mode_1080]", NOS_API.thres)
                                                    if (result or result_1):
                                                        NOS_API.test_cases_results_info.channel_boot_up_state = False
                                                    else:
                                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                        NOS_API.set_error_message("IR")
                                                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                        TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                        
                                                        return
                                                else:
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                    
                                                    return
                                        else:
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                            NOS_API.set_error_message("IR")
                                            error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                                            TEST_CREATION_API.write_log_to_file("STB doesn't Power ON with 2008POWER command")                        
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False


                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                            
                                            return
                                    ##PUT HERE THE COMMAND 2008POWER###
                                    ##NOS_API.test_cases_results_info.channel_boot_up_state = False
                                    
                                    #####
                                    ##############################################
                                    else:
                                        TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_message)
                                        error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                                        error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message
                                                
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        report_file = ""    
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.set_error_message("Video HDMI") 
                                            NOS_API.test_cases_results_info.isTestOK = False
                                    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                    
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                            
                                        return
                                        
                                
                            test_result = "PASS"
                        else:
                            NOS_API.grabber_stop_video_source()
                            time.sleep(1)
                            
                            ## Initialize input interfaces of DUT RT-AV101 device 
                            NOS_API.reset_dut()
                            #time.sleep(2)
                            
                            ## Start grabber device with video on SCART video source
                            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                            time.sleep(WAIT_TO_SWITCH_SCART)

                            ## Check is signal present on SCART
                            if (NOS_API.is_signal_present_on_video_source()):
                                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                NOS_API.set_error_message("Video HDMI")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                            else:
                                TEST_CREATION_API.write_log_to_file("No boot")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                                NOS_API.set_error_message("Não arranca")
                                error_codes = NOS_API.test_cases_results_info.no_boot_error_code
                                error_messages = NOS_API.test_cases_results_info.no_boot_error_message
            else:
                TEST_CREATION_API.write_log_to_file("Wrong MAC")
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.wrong_mac_error_code \
                                                               + "; Error message: " + NOS_API.test_cases_results_info.wrong_mac_error_message \
                                                               + "; MAC: " + NOS_API.test_cases_results_info.mac_using_barcode)
                NOS_API.set_error_message("MAC")
                error_codes = NOS_API.test_cases_results_info.wrong_mac_error_code 
                error_messages = NOS_API.test_cases_results_info.wrong_mac_error_message            
            
            System_Failure = 2
        except Exception as error:
            if(System_Failure == 0):
                System_Failure = System_Failure + 1 
                NOS_API.Inspection = True
                if(System_Failure == 1):
                    try:
                        TEST_CREATION_API.write_log_to_file(error)
                    except: 
                        pass
                    try:
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        TEST_CREATION_API.write_log_to_file(error)
                    except: 
                        pass
                if (NOS_API.configure_power_switch_by_inspection()):
                    if not(NOS_API.power_off()): 
                        TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        NOS_API.set_error_message("Inspection")
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            "",
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                    
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)

                        return
                    time.sleep(10)
                    ## Power on STB with energenie
                    if not(NOS_API.power_on()):
                        TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        NOS_API.set_error_message("Inspection")
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            "",
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        test_result = "FAIL"
                        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                    
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                        
                        return
                    time.sleep(10)
                else:
                    TEST_CREATION_API.write_log_to_file("Incorrect test place name")
                    
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                    NOS_API.set_error_message("Inspection")
                    
                    NOS_API.add_test_case_result_to_file_report(
                                    test_result,
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    error_codes,
                                    error_messages)
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                    report_file = ""
                    if (test_result != "PASS"):
                        report_file = NOS_API.create_test_case_log_file(
                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                        NOS_API.test_cases_results_info.nos_sap_number,
                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                        "",
                                        end_time)
                        NOS_API.upload_file_report(report_file)
                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    test_result = "FAIL"
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    
                
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                    
                    NOS_API.send_report_over_mqtt_test_plan(
                        test_result,
                        end_time,
                        error_codes,
                        report_file)
                    
                    return
                
                NOS_API.Inspection = False
            else:
                test_result = "FAIL"
                TEST_CREATION_API.write_log_to_file(error)
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.grabber_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.grabber_error_message)
                error_codes = NOS_API.test_cases_results_info.grabber_error_code
                error_messages = NOS_API.test_cases_results_info.grabber_error_message
                NOS_API.set_error_message("Inspection")
                System_Failure = 2
        
    NOS_API.add_test_case_result_to_file_report(
                    test_result,
                    "- - - - - - - - - - - - - - - - - - - -",
                    "- - - - - - - - - - - - - - - - - - - -",
                    error_codes,
                    error_messages)
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    report_file = ""
    if (test_result != "PASS"):
        report_file = NOS_API.create_test_case_log_file(
                        NOS_API.test_cases_results_info.s_n_using_barcode,
                        NOS_API.test_cases_results_info.nos_sap_number,
                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                        NOS_API.test_cases_results_info.mac_using_barcode,
                        end_time)
        NOS_API.upload_file_report(report_file)
        NOS_API.test_cases_results_info.isTestOK = False
        
        NOS_API.send_report_over_mqtt_test_plan(
                test_result,
                end_time,
                error_codes,
                report_file)
    
    
    ## Update test result
    TEST_CREATION_API.update_test_result(test_result)

    ## Return DUT to initial state and de-initialize grabber device
    NOS_API.deinitialize()
   