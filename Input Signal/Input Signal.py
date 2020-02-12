# Test name = Input Signal
# Test description = Check signal strength

from datetime import datetime
from time import gmtime, strftime
import time

import TEST_CREATION_API
#import shutil
#shutil.copyfile('\\\\bbtfs\\RT-Executor\\API\\NOS_API.py', 'NOS_API.py')
import NOS_API

## Threshold for signal value
SIGNAL_VALUE_THRESHOLD = 55

BER_THRESHOLD = "1.0E-6"

def runTest():
    

    ## Skip this test case if some previous test failed
    if not(NOS_API.test_cases_results_info.isTestOK):
        TEST_CREATION_API.update_test_result(TEST_CREATION_API.TestCaseResult.FAIL)
        return
        
    System_Failure = 0
    
    while (System_Failure < 2):
        try:
            ## Set test result default to FAIL
            test_result = "FAIL"
            SIGNAL_RESULT= True
            error_codes = ""
            error_messages = ""
            
            modulation = "-"
            frequency =  "-"
            SIGNAL_POWER = "-"
            BER = "-"

            ## Initialize grabber device
            NOS_API.initialize_grabber()        

            ## Start grabber device with video on default video source
            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
            
            if(System_Failure == 1):
                TEST_CREATION_API.send_ir_rc_command("[Exit_Menu]")
                if not(NOS_API.is_signal_present_on_video_source()):
                    test_result = "FAIL"
                    TEST_CREATION_API.write_log_to_file("HDMI NOK")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
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
                                        "",
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
                     
            
            ## Check state of STB
            if (NOS_API.test_cases_results_info.channel_boot_up_state):
                
                ## Set STB to initial state
                TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                time.sleep(2)
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
                
                if not(NOS_API.IN_PT):
                    TEST_CREATION_API.send_ir_rc_command("[INIT]")
                    TEST_CREATION_API.send_ir_rc_command("[SET_LANGUAGE_PT]")
                    TEST_CREATION_API.send_ir_rc_command("[INIT]")
                    NOS_API.IN_PT = True
                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)    
                try:
                    TEST_CREATION_API.grab_picture("menu")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
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
                            
                if(TEST_CREATION_API.compare_pictures("update_screen_" + video_height + "_ref", "menu", "[UPDATE_SCREEN]")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    NOS_API.wait_for_signal_present(500)
                    NOS_API.test_cases_results_info.DidUpgrade = 1
                    time.sleep(5)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
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
                
                    
                
                if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    time.sleep(300)
                    NOS_API.test_cases_results_info.DidUpgrade = 1
                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
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
                            
                                                
                    if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                        time.sleep(120)
                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
                        except: 
                            time.sleep(5)
                            try:
                                TEST_CREATION_API.grab_picture("menu")
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
                            
                            
                        if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
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
                   
                ########################################
                
                TEST_CREATION_API.send_ir_rc_command("[INIT]")
                try:
                    TEST_CREATION_API.grab_picture("menu")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
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
                            
                if not(TEST_CREATION_API.compare_pictures("HDMI_video_ref", "menu", "[HALF_SCREEN]") or TEST_CREATION_API.compare_pictures("no_signal_ref", "menu") or TEST_CREATION_API.compare_pictures("no_signal_ref2", "menu")):
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
                    
                ################################
                    
                
                TEST_CREATION_API.send_ir_rc_command("[SIGNAL_LEVEL_SETTINGS]")
                #macro_signal_level = "[SIGNAL_VALUE]"
                macro_signal_level = "[SIGNAL_VALUE_50_PERCENT]"
                macro_signal_quality = "[SIGNAL_QUALITY_50_PERCENT]"
                ref_image = "signal_value_ref"

            else:    
                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                try:
                    TEST_CREATION_API.grab_picture("menu")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
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
            
                if(TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                    NOS_API.wait_for_signal_present(500)
                    NOS_API.test_cases_results_info.DidUpgrade = 1
                    time.sleep(5)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
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
                            
                
                if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    time.sleep(300)
                    NOS_API.test_cases_results_info.DidUpgrade = 1
                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
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
                            
                                                
                    if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                        time.sleep(120)
                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
                        except: 
                            time.sleep(5)
                            try:
                                TEST_CREATION_API.grab_picture("menu")
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
                            
                            
                        if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
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
                   
                if(TEST_CREATION_API.compare_pictures("Old_SW_ref", "menu", "[Old_SW]") or TEST_CREATION_API.compare_pictures("Cannot_Upgrade_ref", "menu", "[FULL_SCREEN]")):
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
                ########################################
                
                if not(TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "menu") or TEST_CREATION_API.compare_pictures("installation_boot_up_ref2", "menu") or TEST_CREATION_API.compare_pictures("installation_boot_up_ref3", "menu")):
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
                    
                #######################################################################################################
                #TEST_CREATION_API.send_ir_rc_command("[INSTALLATION_BOOT_UP_SEQUENCE_1]")
                TEST_CREATION_API.send_ir_rc_command("[INSTALLATION_BOOT_UP_SEQUENCE_2]")
                try:
                    TEST_CREATION_API.grab_picture("Install")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("Install")
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
            
                if(TEST_CREATION_API.compare_pictures("installation_boot_up_ref","Install") or TEST_CREATION_API.compare_pictures("installation_boot_up_ref2", "Install") or TEST_CREATION_API.compare_pictures("installation_boot_up_ref3", "Install")):
                    TEST_CREATION_API.send_ir_rc_command("[INSTALLATION_BOOT_UP_SEQUENCE_2]")
                    try:
                        TEST_CREATION_API.grab_picture("Install")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("Install")
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
                    
                    if(TEST_CREATION_API.compare_pictures("installation_boot_up_ref","Install") or TEST_CREATION_API.compare_pictures("installation_boot_up_ref2", "Install") or TEST_CREATION_API.compare_pictures("installation_boot_up_ref3", "Install")):
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message) 
                        NOS_API.set_error_message("IR")
                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message
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
    
                start_time = int(time.time())
                while not(TEST_CREATION_API.compare_pictures("Santarem", "Install")):
                    TEST_CREATION_API.send_ir_rc_command("[DOWN]")
                    try:
                        TEST_CREATION_API.grab_picture("Install")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("Install")
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

                    if (TEST_CREATION_API.compare_pictures("Last", "Install")):
                        TEST_CREATION_API.send_ir_rc_command("[20_UP]")
                    timeout = int(time.time()) - start_time
                    if (timeout > 240):
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
                        
                
                TEST_CREATION_API.send_ir_rc_command("[OK]")
                time.sleep(1)
                try:
                    TEST_CREATION_API.grab_picture("Install_1")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("Install_1")
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
                if (TEST_CREATION_API.compare_pictures("Santarem", "Install_1")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]") 
                    time.sleep(1)
                    try:
                        TEST_CREATION_API.grab_picture("Install_2")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("Install_2")
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
                    if (TEST_CREATION_API.compare_pictures("Santarem", "Install_2")):
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                        + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                        NOS_API.set_error_message("IR")
                        error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                        error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                        TEST_CREATION_API.write_log_to_file("STB didn't receive OK Command")                        
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
                time.sleep(3)
                ##############################################################################################
                #macro_signal_level =  "[SIGNAL_VALUE_FTI]"
                macro_signal_level = "[SIGNAL_VALUE_FTI_50_PERCENT]"
                macro_signal_quality = "[SIGNAL_QUALITY_FTI_50_PERCENT]"
                ref_image = "signal_value_fti_ref"
   
            ## Perform grab picture
            try:
                TEST_CREATION_API.grab_picture("signal_value")
            except: 
                time.sleep(5)
                try:
                    TEST_CREATION_API.grab_picture("signal_value")
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
                        
            
            ## Check state of STB
            if (NOS_API.test_cases_results_info.channel_boot_up_state):
                if(TEST_CREATION_API.compare_pictures("signal_value_ref", "signal_value", "[MENU_VALUES]")== False):
                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                    time.sleep(1)
                    TEST_CREATION_API.send_ir_rc_command("[SIGNAL_LEVEL_SETTINGS]")
                    try:
                        TEST_CREATION_API.grab_picture("signal_value")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("signal_value")
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
                
            
            ## Extract text from image
                       
            signal_quality = NOS_API.compare_pictures(ref_image, "signal_value", macro_signal_quality);

            ## Check if signal value higher than threshold
            if (signal_quality >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                test_result = "PASS"

            else:
                NOS_API.display_dialog("Confirme o cabo RF e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                time.sleep(2)
                TEST_CREATION_API.send_ir_rc_command("[LEFT]")
                time.sleep(2)
                TEST_CREATION_API.send_ir_rc_command("[OK]")
                time.sleep(1)
                try:
                    TEST_CREATION_API.grab_picture("Install_3")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("Install_3")
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
                if (TEST_CREATION_API.compare_pictures("Santarem", "Install_3")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]") 
                    time.sleep(1)
                try:
                    TEST_CREATION_API.grab_picture("Install_4")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("Install_4")
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
                if (TEST_CREATION_API.compare_pictures("Santarem", "Install_4")):
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                    NOS_API.set_error_message("IR")
                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message          
                    TEST_CREATION_API.write_log_to_file("STB didn't receive OK Command")                        
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
                time.sleep(3)
                try:
                    try:
                        TEST_CREATION_API.grab_picture("signal_value")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("signal_value")
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
                    
                    ## Extract text from image
                            
                    signal_quality = NOS_API.compare_pictures(ref_image, "signal_value", macro_signal_quality);
                    
                except Exception as error:
                    test_result = "FAIL"
                    TEST_CREATION_API.write_log_to_file(error)
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.grabber_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.grabber_error_message)
                    error_codes = NOS_API.test_cases_results_info.grabber_error_code
                    error_messages = NOS_API.test_cases_results_info.grabber_error_message
                    NOS_API.set_error_message("Inspection")
                    signal_value = 0
                    signal_quality = 0
                    
                ## Check if signal value higher than threshold
                if (signal_quality >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                    test_result = "PASS"
                else:   
                    TEST_CREATION_API.write_log_to_file("Signal quality is lower than threshold")
        
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                    NOS_API.set_error_message("Sem Sinal")
                    error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                    error_messages = NOS_API.test_cases_results_info.input_signal_error_message                                        
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

            if (NOS_API.test_cases_results_info.channel_boot_up_state):
                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                time.sleep(2)
                TEST_CREATION_API.send_ir_rc_command("[MOD_MENU]")
                try:
                    TEST_CREATION_API.grab_picture("menu_values")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu_values")
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
            
                
                if(TEST_CREATION_API.compare_pictures("menu_values_ref", "menu_values", "[MENU_VALUES]")== False):
                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                    time.sleep(1)
                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                    time.sleep(2)
                    TEST_CREATION_API.send_ir_rc_command("[MOD_MENU_BEGIN]")
                
                modulation = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_MOD]", "[OCR_FILTER]", "stb_mod")
                NOS_API.test_cases_results_info.modulation = str(modulation)
                frequency = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_FREQ]", "[OCR_FILTER]", "stb_freq")
                NOS_API.test_cases_results_info.freq = str(frequency)
                power = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_POW]", "[OCR_FILTER]", "stb_power")
                BER = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_BER]", "[OCR_FILTER]", "stb_ber")
                BER = NOS_API.fix_ber(BER)
                NOS_API.test_cases_results_info.ber = str(BER)
                
            else:
                TEST_CREATION_API.send_ir_rc_command("[OK]")
                
                result = NOS_API.wait_for_multiple_pictures(["Channels_list_ref"], 40, ["[Channels_List]"], [80])
                
                if (result != 0):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    
                    result = NOS_API.wait_for_multiple_pictures(["Channels_list_ref"], 40, ["[Channels_List]"], [80])
                    if (result != 0):
                        TEST_CREATION_API.write_log_to_file("STB Blocks")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.block_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.block_error_message)
                        NOS_API.set_error_message("STB bloqueou")
                        error_codes = NOS_API.test_cases_results_info.block_error_code
                        error_messages = NOS_API.test_cases_results_info.block_error_message
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        test_result = "FAIL"
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
                time.sleep(5)
                
                if not(NOS_API.grab_picture("Channels_List")):
                   TEST_CREATION_API.write_log_to_file("HDMI NOK")
                   NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                           + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                   NOS_API.set_error_message("Video HDMI")
                   error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                   error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                   test_result = "FAIL"
                   NOS_API.add_test_case_result_to_file_report(
                                                   test_result,
                                                   "- - - - - - - - - - - - - - - - - - - -",
                                                   ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                   error_codes,
                                                   error_messages)
                   end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                   report_file = ""    
                
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
                   
                   return
              
                if(TEST_CREATION_API.compare_pictures("Channels_list_ref", "Channels_List", "[Channels_List]")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    if not(NOS_API.grab_picture("Channels_List_2")):
                        TEST_CREATION_API.write_log_to_file("HDMI NOK")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                        NOS_API.set_error_message("Video HDMI")
                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                        test_result = "FAIL"
                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        report_file = ""    
                        
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
                        
                        return
                    if(TEST_CREATION_API.compare_pictures("Channels_list_ref", "Channels_List_2", "[Channels_List]")):
                        TEST_CREATION_API.write_log_to_file("STB Blocks")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.block_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.block_error_message)
                        NOS_API.set_error_message("STB bloqueou")
                        error_codes = NOS_API.test_cases_results_info.block_error_code
                        error_messages = NOS_API.test_cases_results_info.block_error_message
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        test_result = "FAIL"
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
                
                try:
                    TEST_CREATION_API.grab_picture("menu")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
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
            
                if(TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    NOS_API.wait_for_signal_present(500)
                    time.sleep(5)
                    NOS_API.wait_for_signal_present(600)
                    NOS_API.test_cases_results_info.DidUpgrade = 1
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    if not(TEST_CREATION_API.is_signal_present_on_video_source()):
                        time.sleep(3)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
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

                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                if(video_height != "720"):
                    if(video_height == "1080"):
                        pic_macro = "[RT_RK_LOGO_1080]"
                    elif(video_height == "576"):
                        pic_macro = "[RT_RK_LOGO_576]"
                    else:
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
                
                ############### Pode haver falhas devido a imagens capturadas estarem desviadas
                
                    if(TEST_CREATION_API.compare_pictures("HDMI_video_" + video_height +"_ref", "menu", pic_macro)):
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
                    
                
                        try:
                            TEST_CREATION_API.grab_picture("menu")
                        except: 
                            time.sleep(5)
                            try:
                                TEST_CREATION_API.grab_picture("menu")
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
                
                
                    else:
                        TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_message)
                        error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                        error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message

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
             
                if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    time.sleep(300)
                    NOS_API.test_cases_results_info.DidUpgrade = 1
                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
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
                
                                                
                    if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                        time.sleep(120)
                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu")
                        except: 
                            time.sleep(5)
                            try:
                                TEST_CREATION_API.grab_picture("menu")
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
                    
                            
                        if(TEST_CREATION_API.compare_pictures("blue_ref1", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("blue_ref2", "menu", "[OLD_ZON]") or TEST_CREATION_API.compare_pictures("update_ref", "menu") or TEST_CREATION_API.compare_pictures("update_screen_ref", "menu", "[UPDATE_SCREEN]")):
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
                time.sleep(2)
                
                if(TEST_CREATION_API.compare_pictures("Cannot_Upgrade_ref", "menu", "[FULL_SCREEN]")):
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
                
                try:
                    TEST_CREATION_API.grab_picture("screen")
                except:
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("screen")
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
                if(TEST_CREATION_API.compare_pictures("black_720_ref", "screen")):
                    TEST_CREATION_API.send_ir_rc_command("[CH+]")
                    time.sleep(2)
                    TEST_CREATION_API.send_ir_rc_command("[CH-]")
                    time.sleep(2)
                    TEST_CREATION_API.send_ir_rc_command(NOS_API.SD_CHANNEL)
                    time.sleep(1)
                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                    
                    
                    try:
                        TEST_CREATION_API.grab_picture("screen")
                    except:
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("screen")
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
                        
                        
                    if(TEST_CREATION_API.compare_pictures("black_720_ref", "screen")):
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
                TEST_CREATION_API.send_ir_rc_command("[MOD_MENU_BEGIN]")
                
                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                time.sleep(3)
                
                try:
                    TEST_CREATION_API.grab_picture("menu_values")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu_values")
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
            
                
                if(TEST_CREATION_API.compare_pictures("menu_values_ref", "menu_values", "[SIGNAL_VALUES_MENU]")== False):
                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                    time.sleep(4)
                    TEST_CREATION_API.send_ir_rc_command("[MOD_MENU_BEGIN]")
                    
                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                    time.sleep(3)
                
                    try:
                        TEST_CREATION_API.grab_picture("menu_values_1")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("menu_values_1")
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
                
                 
                    if(TEST_CREATION_API.compare_pictures("menu_values_ref", "menu_values_1", "[SIGNAL_VALUES_MENU]")== False):
                        
                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                        time.sleep(4)
                        TEST_CREATION_API.send_ir_rc_command("[MOD_MENU_BEGIN]")
                        
                        TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                        time.sleep(3)
                    
                        try:
                            TEST_CREATION_API.grab_picture("menu_values_2")
                        except: 
                            time.sleep(5)
                            try:
                                TEST_CREATION_API.grab_picture("menu_values_2")
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
                    
                        if(TEST_CREATION_API.compare_pictures("menu_values_ref", "menu_values_2", "[SIGNAL_VALUES_MENU]")== False):
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
                
                try:
                    TEST_CREATION_API.grab_picture("menu_values")
                except: 
                    time.sleep(5)
                    try:
                        TEST_CREATION_API.grab_picture("menu_values")
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

                modulation = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_MOD]", "[OCR_FILTER]", "stb_mod")
                NOS_API.test_cases_results_info.modulation = str(modulation)
                frequency = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_FREQ]", "[OCR_FILTER]", "stb_freq")
                NOS_API.test_cases_results_info.freq = str(frequency)
                power = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_POW]", "[OCR_FILTER]", "stb_power")
                BER = TEST_CREATION_API.OCR_recognize_text("menu_values", "[STB_BER]", "[OCR_FILTER]", "stb_ber")
                BER = NOS_API.fix_ber(BER)
                NOS_API.test_cases_results_info.ber = str(BER)
            
            TEST_CREATION_API.write_log_to_file("The stb Modulation is: " + modulation)
            TEST_CREATION_API.write_log_to_file("The stb Frequency is: " + frequency)
            TEST_CREATION_API.write_log_to_file("The stb Signal Power is: " + power)
            TEST_CREATION_API.write_log_to_file("The stb BER is: " + BER)
            
            TEST_CREATION_API.send_ir_rc_command("[EXIT]")
            
            try:
                result_float = True
                SIGNAL_POWER= float(power)
                NOS_API.test_cases_results_info.power = str(SIGNAL_POWER)
            except ValueError:
                result_float= False
                    
            if(power == ""  or result_float == False):
                
                TEST_CREATION_API.write_log_to_file("No Signal")
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                       + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                NOS_API.set_error_message("Sem Sinal")
                error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                error_messages = NOS_API.test_cases_results_info.input_signal_error_message 
                SIGNAL_RESULT = False
                NOS_API.test_cases_results_info.power = "-"
                test_result = "FAIL"
            else:
                          
                if(SIGNAL_POWER < 50 or SIGNAL_POWER > 70):
                    TEST_CREATION_API.write_log_to_file("Signal Power is outside acceptable data range")
            
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.input_signal_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.input_signal_error_message)
                    NOS_API.set_error_message("Sem Sinal")
                    error_codes = NOS_API.test_cases_results_info.input_signal_error_code
                    error_messages = NOS_API.test_cases_results_info.input_signal_error_message 
                    SIGNAL_RESULT = False
                    test_result = "FAIL"
                    modulation = "-"
                    frequency =  "-"
                    
                    BER = "-"
            
            if(SIGNAL_RESULT):        
                if not(NOS_API.check_ber(BER, BER_THRESHOLD)):
                    test_result = "FAIL"
                    TEST_CREATION_API.write_log_to_file("BER fail")
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ber_fail_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.ber_fail_error_message)
                    NOS_API.set_error_message("BER") 
                    error_codes = NOS_API.test_cases_results_info.ber_fail_error_code
                    error_messages = NOS_API.test_cases_results_info.ber_fail_error_message
                    
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
                    "- - - - - - - - - " + str(SIGNAL_POWER) + " " + str(BER) + " - - - - - - " + str(modulation) + " " + str(frequency) + " -",
                    "- - - - - - - - - >50<70 <1.0E-6 - - - - - - - - -",
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
