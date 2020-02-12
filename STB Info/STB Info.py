# Test name = Serial Number
# Test description = Check S/N from menu with scanned S/N, log nagraguide version and sw version

from datetime import datetime
from time import gmtime, strftime
import time

import TEST_CREATION_API
#import shutil
#shutil.copyfile('\\\\bbtfs\\RT-Executor\\API\\NOS_API.py', 'NOS_API.py')
import NOS_API

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
            test_result_sn = False
            error_codes = ""
            error_messages = ""

            FIRMWARE_VERSION_PROD = NOS_API.Firmware_Version_DCI_7211
            nagra_guide_version_Prod = NOS_API.Nagra_Guide_Version_DCI_7211
            logistic_serial_number = "-"
            nagra_guide_version = "-"
            firmware_version = "-"
            power_percentage = "-"
            signal_quality_percentage = "-"
            cas_id_number = "-"
            sc_number = "-"


            ## Get scanned STB Barcode
            scanned_serial_number = NOS_API.test_cases_results_info.s_n_using_barcode
            
            TEST_CREATION_API.send_ir_rc_command("[EXIT_WITHOUT_DELAY]")

            ## Initialize grabber device
            NOS_API.initialize_grabber()

            ## Start grabber device with video on default video source
            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
            #time.sleep(2)
            ## Zap to channel
            if(System_Failure == 1):
                TEST_CREATION_API.send_ir_rc_command("[Exit_Menu]")
                time.sleep(2)
                ## Zap to service
                TEST_CREATION_API.send_ir_rc_command("[CH_1]")

            ## Navigate to the Info ZON box menu
            TEST_CREATION_API.send_ir_rc_command("[INFO_ZON_BOX_MENU_T7211]")
            
            try:
                ## Perform grab picture
                try:
                    TEST_CREATION_API.grab_picture("zon_box_data")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("zon_box_data")
                    except:
                        
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
                
                if not(TEST_CREATION_API.compare_pictures("zon_box_data_ref", "zon_box_data", "[SN_MENU]")):
                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                    TEST_CREATION_API.send_ir_rc_command("[EXIT_WITHOUT_DELAY]")
                    time.sleep(1)
                    TEST_CREATION_API.send_ir_rc_command("[INFO_ZON_BOX_MENU_T7211]")
                    time.sleep(1)
                    try:
                        TEST_CREATION_API.grab_picture("zon_box_data")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("zon_box_data")
                        except:
                            
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
                
                if not(TEST_CREATION_API.compare_pictures("zon_box_data_ref", "zon_box_data", "[SN_MENU]")):
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
                    
                ## Extract serial number from image
                logistic_serial_number = NOS_API.remove_whitespaces(TEST_CREATION_API.OCR_recognize_text("zon_box_data", "[SERIAL_NUMBER]", "[OCR_FILTER]"))
            except Exception as error:
                TEST_CREATION_API.write_log_to_file(error)
                logistic_serial_number = "-"
                            
            NOS_API.test_cases_results_info.s_n = logistic_serial_number

            TEST_CREATION_API.write_log_to_file("Logistic serial number (from menu):\t" + logistic_serial_number, "logistic_serial_number.txt")

            ## Check if logistic serial number is the same as scanned serial number
           
            if (NOS_API.ignore_zero_letter_o_during_comparation(logistic_serial_number, scanned_serial_number)):


                ## Set test result to PASS
                test_result_sn = True
                
                try:
                    ## Extract NagraGuide version from image
                    nagra_guide_version = TEST_CREATION_API.OCR_recognize_text("zon_box_data", "[NAGRA_GUIDE_VERSION]", "[OCR_FILTER]", "nagra_guide_version")
                    
                    NOS_API.test_cases_results_info.nagra_guide_version = nagra_guide_version
                    
                    TEST_CREATION_API.write_log_to_file("The extracted nagra guide version is: " + nagra_guide_version)
                    if not(nagra_guide_version == nagra_guide_version_Prod):
                        test_result_sn = False
                        TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message) 
                        NOS_API.set_error_message("Não Actualiza") 
                        error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                        error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                        test_result = "FAIL"
                    ## Extract SW Version from image
                    firmware_version = TEST_CREATION_API.OCR_recognize_text("zon_box_data", "[FIRMWARE_VERSION]", "[OCR_FILTER]", "firmware_version")
                    NOS_API.test_cases_results_info.firmware_version = firmware_version
                    
                    TEST_CREATION_API.write_log_to_file("The extracted firmware version is: " + firmware_version)
                    if not(firmware_version == FIRMWARE_VERSION_PROD):
                        test_result_sn = False
                        TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message) 
                        NOS_API.set_error_message("Não Actualiza") 
                        error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                        error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                        test_result = "FAIL"
                    
                    
                except Exception as error:
                    TEST_CREATION_API.write_log_to_file(error)
                    nagra_guide_version = "-"
                    firmware_version = "-"
                

            else:
                TEST_CREATION_API.write_log_to_file("Logistic serial number is not the same as scanned serial number")

                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_s_n_error_code \
                                                           + "; Error message: " + NOS_API.test_cases_results_info.wrong_s_n_error_message \
                                                           + "; OCR: " + str(logistic_serial_number))
                error_codes = NOS_API.test_cases_results_info.wrong_s_n_error_code
                error_messages = NOS_API.test_cases_results_info.wrong_s_n_error_message
                NOS_API.set_error_message("S/N")
                
                
                
                
            ###############################################################################################################################################
            
            if(test_result_sn):
                
                ## Navigate to the SC information menu from live mode

                TEST_CREATION_API.send_ir_rc_command("[RIGHT]")
                
                try:
                    TEST_CREATION_API.grab_picture("stb_info")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("stb_info")
                    except:
                        
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
        
                if not(TEST_CREATION_API.compare_pictures("stb_info_ref", "stb_info", "[Page_Number]")):
                    TEST_CREATION_API.send_ir_rc_command("[REDO_Info]")
                    try:
                        TEST_CREATION_API.grab_picture("stb_info")
                    except:
                        
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
                if not(TEST_CREATION_API.compare_pictures("stb_info_ref", "stb_info", "[Page_Number]")):
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
                
                power_percentage = TEST_CREATION_API.OCR_recognize_text("stb_info", "[STB_POW%]", "[OCR_FILTER]", "stb_pow%")
                NOS_API.test_cases_results_info.power_percent = str(power_percentage)

                TEST_CREATION_API.write_log_to_file("The stb Power(%) is: " + power_percentage)
                
                TEST_CREATION_API.send_ir_rc_command("[RIGHT]")
                
                ## Perform grab picture
                try:
                    TEST_CREATION_API.grab_picture("sc_info")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("sc_info")
                    except:
                        
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
                
                if not(TEST_CREATION_API.compare_pictures("File", "sc_info", "[Page_Number]")):
                    TEST_CREATION_API.send_ir_rc_command("[REDO_SC]")
                    try:
                        TEST_CREATION_API.grab_picture("sc_info")
                    except:
                        
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
                if not(TEST_CREATION_API.compare_pictures("File", "sc_info", "[Page_Number]")):
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
                    
                video_result = NOS_API.mask_and_compare_pictures("File", "sc_info", "File-MASK");
        
                ## Check is SC not detected
                if (video_result >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                
                    NOS_API.display_dialog("Reinsira o cart\xe3o e de seguida pressiona Continuar", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                    
                    TEST_CREATION_API.send_ir_rc_command("[REDO_SC]")
                    
                    ## Perform grab picture
                    try:
                        TEST_CREATION_API.grab_picture("sc_info")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("sc_info")
                        except:
                            
                            TEST_CREATION_API.write_log_to_file("STB lost Signal after operator re insert SmartCard.Possible Reboot.")
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
                    
                    if not(TEST_CREATION_API.compare_pictures("File", "sc_info", "[Page_Number]")):
                        TEST_CREATION_API.send_ir_rc_command("[REDO_SC]")
                        try:
                            TEST_CREATION_API.grab_picture("sc_info")
                        except:
                            
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
                    
                    if not(TEST_CREATION_API.compare_pictures("File", "sc_info", "[Page_Number]")):
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
                    
                    video_result = NOS_API.mask_and_compare_pictures("File", "sc_info", "File-MASK");
            
                    ## Check is SC not detected
                    if (video_result >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                        
                    ####################################################################################################
                        TEST_CREATION_API.write_log_to_file("Smart card is not detected")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.sc_not_detected_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.sc_not_detected_error_message \
                                                                + "; V: " + str(video_result))
                        NOS_API.set_error_message("SmartCard")     
                        error_codes = NOS_API.test_cases_results_info.sc_not_detected_error_code
                        error_messages = NOS_API.test_cases_results_info.sc_not_detected_error_message
                    #####################################################################################################
                    else:
                        
                        ## Extract text from image
                        sc_number = TEST_CREATION_API.OCR_recognize_text("sc_info", "[SC_NUMBER]", "[OCR_FILTER]", "sc_number")
                                
        
                        cas_id_number =  NOS_API.fix_extracted_string(TEST_CREATION_API.OCR_recognize_text("sc_info", "[CAS_ID_NUMBER]", "[OCR_FILTER]", "cas_id_number"))
                        
                        NOS_API.test_cases_results_info.sc_number = sc_number
                        NOS_API.test_cases_results_info.cas_id_number = cas_id_number
            
                        TEST_CREATION_API.write_log_to_file("The extracted sc number is: " + sc_number)
                        TEST_CREATION_API.write_log_to_file("The extracted cas id number is: " + cas_id_number)
            
                        NOS_API.update_test_slot_comment("SC number: " + NOS_API.test_cases_results_info.sc_number \
                                                                #+ "; sc version: " + NOS_API.test_cases_results_info.sc_version \
                                                                + "; cas id number: " + NOS_API.test_cases_results_info.cas_id_number)
            
                        ## System must compare CAS ID number with the CAS ID number previuosly scanned by barcode scanner
                        if (NOS_API.ignore_zero_letter_o_during_comparation(cas_id_number, NOS_API.test_cases_results_info.cas_id_using_barcode)):
                            test_result = "PASS"
                            NOS_API.test_cases_results_info.correct_cas_id_number = True
                        else:
                            TEST_CREATION_API.write_log_to_file("CAS ID number and CAS ID number previuosly scanned by barcode scanner is not the same")
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_cas_id_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.wrong_cas_id_error_message \
                                                                + "; OCR: " + str(cas_id_number))
                            NOS_API.set_error_message("CAS ID")
                            error_codes = NOS_API.test_cases_results_info.wrong_cas_id_error_code
                            error_messages = NOS_API.test_cases_results_info.wrong_cas_id_error_message
            
                    TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                    
                else:
                        
                    ## Extract text from image
                    sc_number = TEST_CREATION_API.OCR_recognize_text("sc_info", "[SC_NUMBER]", "[OCR_FILTER]", "sc_number")
                            

                    cas_id_number =  NOS_API.fix_extracted_string(TEST_CREATION_API.OCR_recognize_text("sc_info", "[CAS_ID_NUMBER]", "[OCR_FILTER]", "cas_id_number"))
                    
                    NOS_API.test_cases_results_info.sc_number = sc_number
                    NOS_API.test_cases_results_info.cas_id_number = cas_id_number
        
                    TEST_CREATION_API.write_log_to_file("The extracted sc number is: " + sc_number)
                    TEST_CREATION_API.write_log_to_file("The extracted cas id number is: " + cas_id_number)
        
                    NOS_API.update_test_slot_comment("SC number: " + NOS_API.test_cases_results_info.sc_number \
                                                            #+ "; sc version: " + NOS_API.test_cases_results_info.sc_version \
                                                            + "; cas id number: " + NOS_API.test_cases_results_info.cas_id_number)
        
                    ## System must compare CAS ID number with the CAS ID number previuosly scanned by barcode scanner
                    if (NOS_API.ignore_zero_letter_o_during_comparation(cas_id_number, NOS_API.test_cases_results_info.cas_id_using_barcode)):
                        test_result = "PASS"
                        NOS_API.test_cases_results_info.correct_cas_id_number = True
                    else:
                        TEST_CREATION_API.write_log_to_file("CAS ID number and CAS ID number previuosly scanned by barcode scanner is not the same")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_cas_id_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.wrong_cas_id_error_message \
                                                            + "; OCR: " + str(cas_id_number))
                        NOS_API.set_error_message("CAS ID")
                        error_codes = NOS_API.test_cases_results_info.wrong_cas_id_error_code
                        error_messages = NOS_API.test_cases_results_info.wrong_cas_id_error_message
                    
                    TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
            
            System_Failure = 2
        ###############################################################################################################################################
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
                     "- - " + str(power_percentage) + " " + str(signal_quality_percentage) + " - - - - - - - " + str(logistic_serial_number) + " " + str(cas_id_number) + " " + str(firmware_version) + " " + str(nagra_guide_version) + " " + str(sc_number) + " - - - -",
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
