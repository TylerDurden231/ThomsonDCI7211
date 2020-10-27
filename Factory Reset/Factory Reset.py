# -*- coding: utf-8 -*-
# Test name = Measure Boot Time
# Test description = Perform factory reset and measure time to display first image after factory reset

from datetime import datetime
from time import gmtime, strftime
import time

import TEST_CREATION_API
#import shutil
#shutil.copyfile('\\\\bbtfs\\RT-Executor\\API\\NOS_API.py', 'NOS_API.py')
import NOS_API

## Wait time to display first image after factory reset
TIME_COUNTER = 70

## Constant multiplier used for conversion from seconds to milliseconds
MS_MULTIPLIER = 1000

def runTest():
    System_Failure = 0
    
     ## Skip this test case if some previous test failed
    if not(NOS_API.test_cases_results_info.isTestOK):
        TEST_CREATION_API.update_test_result(TEST_CREATION_API.TestCaseResult.FAIL)
        #TEST_CREATION_API.write_log_to_file("Skip this test case if some previous test failed")
        return
    
    while (System_Failure < 2):
        try:
            ## Set test result default to FAIL
            test_result = "FAIL"
            test_result_boot = False
            boot_counter = "-"
            error_codes = ""
            error_messages = ""

            ## Initialize grabber device
            NOS_API.initialize_grabber()

            ## Start grabber device with video on default video source
            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
            #time.sleep(1)
            if(System_Failure == 1):
                if not(NOS_API.is_signal_present_on_video_source()):
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
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                        
                
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                    return
            
                TEST_CREATION_API.send_ir_rc_command("[Exit_Menu]")
            
            if (TEST_CREATION_API.is_signal_present_on_video_source()):
                ## Set STB in initial state
                TEST_CREATION_API.send_ir_rc_command("[INIT]")
            
                ## Navigate to the factory reset
                TEST_CREATION_API.send_ir_rc_command("[FACTORY_RESET_T7211]")
            
                if not(NOS_API.grab_picture("Factory_Reset")):            
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
                
                #if not(TEST_CREATION_API.compare_pictures("factory_reset_ref", "Factory_Reset", "[FACTORY_RESET_MENU]")):
                if not(TEST_CREATION_API.compare_pictures("Factory_Reset_720_ref", "Factory_Reset", "[FACTORY_RESET_MENU]") or TEST_CREATION_API.compare_pictures("Factory_Reset_720_ref_2", "Factory_Reset", "[FACTORY_RESET_MENU]")):
                    TEST_CREATION_API.send_ir_rc_command("[LEFT]")
                    TEST_CREATION_API.send_ir_rc_command("[LEFT]")
                    TEST_CREATION_API.send_ir_rc_command("[INIT]")
                    time.sleep(2)
                    
                    ## Navigate to the factory reset
                    TEST_CREATION_API.send_ir_rc_command("[FACTORY_RESET_T7211]")
                    
                    if not(NOS_API.grab_picture("Factory_Reset_1")):            
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
                    
                    #if not(TEST_CREATION_API.compare_pictures("factory_reset_ref", "Factory_Reset_1", "[FACTORY_RESET_MENU]")): 
                    if not(TEST_CREATION_API.compare_pictures("Factory_Reset_720_ref", "Factory_Reset_1", "[FACTORY_RESET_MENU]") or TEST_CREATION_API.compare_pictures("Factory_Reset_720_ref_2", "Factory_Reset", "[FACTORY_RESET_MENU]")):
                        TEST_CREATION_API.write_log_to_file("Doesn't Navigate to right place")
                        NOS_API.set_error_message("Navegação")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                        error_codes = NOS_API.test_cases_results_info.navigation_error_code
                        error_messages = NOS_API.test_cases_results_info.navigation_error_message
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
                    
                ## Perform factory reset
                TEST_CREATION_API.send_ir_rc_command("[OK_WITHOUT_DELAY]")
                
            
                ## Convert start time to milliseconds
                start_time_in_ms = int(time.time() * MS_MULTIPLIER)
            
                ## Check is FTI displayed after factory reset
                if (NOS_API.wait_for_multiple_pictures(["fti_ref"], TIME_COUNTER, ["[FULL_SCREEN]"], [TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD]) != -1):

            
                    ## Get time(in milliseconds) required to display first image after factory reset
                    boot_counter = int(time.time() * MS_MULTIPLIER) - start_time_in_ms
            
                    TEST_CREATION_API.write_log_to_file("Duration of displaying first image after factory reset: " + str(boot_counter) + "ms", "measured_time.txt")
                    NOS_API.update_test_slot_comment("Duration of displaying first image after factory reset: " + str(boot_counter) + "ms")
                    NOS_API.test_cases_results_info.boot_measured_time = str(boot_counter)
            
                    ## Set test result to PASS
                    test_result_boot = True
                else:
                    TEST_CREATION_API.write_log_to_file("Time out is over")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.measure_boot_time_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.measure_boot_time_error_message)
                    NOS_API.set_error_message("Factory Reset")
                    error_codes = NOS_API.test_cases_results_info.measure_boot_time_error_code
                    error_messages = NOS_API.test_cases_results_info.measure_boot_time_error_message
            
            else:
                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                       + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                NOS_API.set_error_message("Video HDMI")   
                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                
                       
        ################################################## After Factory Reset ############################################################# 

            if(test_result_boot):
                  
                if (NOS_API.display_custom_dialog("O Led Power est\xe1 Verde?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                    if (NOS_API.display_custom_dialog("O Led Rede est\xe1 Ligado? Pressiona a tecla 'Power' da STB", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):#TEST_CREATION_API.display_message("Pressiona a tecla 'Power' da STB e de seguida pressiona OK no monitor",  TEST_CREATION_API.DEFAULT_MESSAGE_WAIT_TIME, TEST_CREATION_API.MessageWindowButtons.CONTINUE)
                        #NOS_API.display_custom_dialog("Pressiona a tecla 'Power' da STB e de seguida pressiona Continuar", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                        
                        time.sleep(2)
                        
                        if (TEST_CREATION_API.is_signal_present_on_video_source()):
                            TEST_CREATION_API.write_log_to_file("Power button NOK")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_button_nok_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.power_button_nok_error_message)
                            #NOS_API.set_error_message("Bot\xf5es")  
                            NOS_API.set_error_message("Botões")
                            error_codes = NOS_API.test_cases_results_info.power_button_nok_error_code
                            error_message = NOS_API.test_cases_results_info.power_button_nok_error_message
                        else:
                            if (NOS_API.display_custom_dialog("O Led Power est\xe1 Vermelho?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                                if (NOS_API.display_custom_dialog("O display est\xe1 ligado?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                                    test_result = "PASS"
                                    if (NOS_API.configure_power_switch_by_inspection()):
                                        NOS_API.power_off() 
                                else:
                                    TEST_CREATION_API.write_log_to_file("Display NOK")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.display_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.display_nok_error_message)
                                    NOS_API.set_error_message("Display")
                                    error_codes = NOS_API.test_cases_results_info.display_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.display_nok_error_message
                            else:
                                TEST_CREATION_API.write_log_to_file("Led POWER Red NOK")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.led_power_red_nok_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.led_power_red_nok_error_message)
                                NOS_API.set_error_message("Led's")
                                error_codes = NOS_API.test_cases_results_info.led_power_red_nok_error_code
                                error_messages = NOS_API.test_cases_results_info.led_power_red_nok_error_message
                    
                    else:
                        TEST_CREATION_API.write_log_to_file("Led Net NOK")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.led_net_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.led_net_nok_error_message)
                        NOS_API.set_error_message("Led's")
                        error_codes = NOS_API.test_cases_results_info.led_net_nok_error_code
                        error_message = NOS_API.test_cases_results_info.led_net_nok_error_message
                    
                else:
                    TEST_CREATION_API.write_log_to_file("Led POWER green NOK")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.led_power_green_nok_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.led_power_green_nok_error_message)
                    NOS_API.set_error_message("Led's")
                    error_codes = NOS_API.test_cases_results_info.led_power_green_nok_error_code
                    error_message = NOS_API.test_cases_results_info.led_power_green_nok_error_message
        ####################################################################################################################################
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
                    "- - - - - - - - - - - - - - - - - - - " + str(boot_counter),
                    "- - - - - - - - - - - - - - - - - - - -",
                    error_codes,
                    error_messages)
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    report_file = NOS_API.create_test_case_log_file(
                    NOS_API.test_cases_results_info.s_n_using_barcode,
                    NOS_API.test_cases_results_info.nos_sap_number,
                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                    NOS_API.test_cases_results_info.mac_using_barcode,
                    end_time) 
    NOS_API.upload_file_report(report_file)

    ## Update test result
    TEST_CREATION_API.update_test_result(test_result)

    ## Return DUT to initial state and de-initialize grabber device
    NOS_API.deinitialize()
    
    NOS_API.send_report_over_mqtt_test_plan(
                test_result,
                end_time,
                error_codes,
                report_file)
   