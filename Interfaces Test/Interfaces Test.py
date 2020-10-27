# Test name = HDMI Video Output 720p
# Test description = Analyze video on HDMI 720p

from datetime import datetime
from time import gmtime, strftime
import time

import TEST_CREATION_API
#import shutil
#shutil.copyfile('\\\\bbtfs\\RT-Executor\\API\\NOS_API.py', 'NOS_API.py')
import NOS_API

## Max record video time in miliseconds
MAX_RECORD_VIDEO_TIME = 2000

## Max record audio time in miliseconds
MAX_RECORD_AUDIO_TIME = 2000

## Time to switch from HDMI to SCART in seconds
WAIT_TO_SWITCH_SCART = 6

THRESHOLD = 70

def runTest():
    System_Failure = 0
    
     ## Skip this test case if some previous test failed
    if not(NOS_API.test_cases_results_info.isTestOK):
        TEST_CREATION_API.update_test_result(TEST_CREATION_API.TestCaseResult.FAIL)
        return
        
    while (System_Failure < 2):
        try:
            ## Set test result default to FAIL
            test_result = "FAIL"
            test_result_output = False
            test_result_quality = False
            error_codes = ""
            error_messages = ""
            HDMI_Result = False
            
            test_result_SCART_video = False        
            SCART_Result = False
            
            COMPOSITE_Result = False
            
            ANALOG_Result = False
            
            test_result_SPDIF_COAX = False
            SPDIF_Result = False
            
            test_result_SD = False
            error_command_telnet = False
            stb_state = False
            
            test_result_res = False
            test_result_hd = False
            pqm_analyse_check = True
            hd_counter = 0
            sd_ch_counter = 0

            ## Initialize grabber device
            NOS_API.initialize_grabber()

            
            ####################################################### 720p  HDMI Video #########################################################################
            
            ## Start grabber device with video on default video source
            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
            TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.HDMI1)
            
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
                
            ## Set volume to max
            TEST_CREATION_API.send_ir_rc_command("[VOL_MIN]")
            
            ## Set volume to half, because if vol is max, signal goes in saturation
            TEST_CREATION_API.send_ir_rc_command("[VOL_PLUS_HALF]")
            
            ## Zap to service
            TEST_CREATION_API.send_ir_rc_command("[CH_1]")

            time.sleep(NOS_API.MAX_ZAP_TIME)
            
            if not (NOS_API.is_signal_present_on_video_source()):
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
                
            ## Record video with duration of recording (10 seconds)
            NOS_API.record_video("video", MAX_RECORD_VIDEO_TIME)

            ## Instance of PQMAnalyse type
            pqm_analyse = TEST_CREATION_API.PQMAnalyse()

            ## Set what algorithms should be checked while analyzing given video file with PQM.
            # Attributes are set to false by default.
            pqm_analyse.black_screen_activ = True
            pqm_analyse.blocking_activ = True
            pqm_analyse.freezing_activ = True

            # Name of the video file that will be analysed by PQM.
            pqm_analyse.file_name = "video"

            ## Analyse recorded video
            analysed_video = TEST_CREATION_API.pqm_analysis(pqm_analyse)

            if (pqm_analyse.black_screen_detected == TEST_CREATION_API.AlgorythmResult.DETECTED):
                pqm_analyse_check = False
                NOS_API.set_error_message("Video HDMI")
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_code \
                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_code)
                error_codes = NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_code
                error_messages = NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_message                    

            if (pqm_analyse.blocking_detected == TEST_CREATION_API.AlgorythmResult.DETECTED):
                pqm_analyse_check = False
                NOS_API.set_error_message("Video HDMI")
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_code \
                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_message)
                if (error_codes == ""):
                    error_codes = NOS_API.test_cases_results_info.hdmi_720p_blocking_error_code
                else:
                    error_codes = error_codes + " " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_code
                        
                if (error_messages == ""):
                    error_messages = NOS_API.test_cases_results_info.hdmi_720p_blocking_error_message
                else:
                    error_messages = error_messages + " " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_message        
                           
            if (pqm_analyse.freezing_detected == TEST_CREATION_API.AlgorythmResult.DETECTED):
                pqm_analyse_check = False
                NOS_API.set_error_message("Video HDMI")
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code \
                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message)
                if (error_codes == ""):
                    error_codes = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code
                else:
                    error_codes = error_codes + " " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code
                        
                if (error_messages == ""):
                    error_messages = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message
                else:
                    error_messages = error_messages + " " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message
       
            if not(pqm_analyse_check): 
                NOS_API.set_error_message("Video HDMI")
                NOS_API.add_test_case_result_to_file_report(
                                test_result,
                                "- - - - - - - - - - - - - - - - - - - -",
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
                
            if (analysed_video):            
                test_result_output = True
            else:
                TEST_CREATION_API.write_log_to_file("Could'n't Record Video")
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.grabber_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.grabber_error_message)
                error_codes = NOS_API.test_cases_results_info.grabber_error_code
                error_messages = NOS_API.test_cases_results_info.grabber_error_message
                NOS_API.set_error_message("Inspection")
                
                NOS_API.add_test_case_result_to_file_report(
                                test_result,
                                "- - - - - - - - - - - - - - - - - - - -",
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
        
        ############################################## 720p HDMI Video Quality ##########################################################
        
            if(test_result_output):
            
                video_result = 0
            
                try:
                    ## Perform grab picture
                    try:
                        TEST_CREATION_API.grab_picture("HDMI_video")
                    except: 
                        time.sleep(5)
                        try:
                            TEST_CREATION_API.grab_picture("HDMI_video")
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
            
                    ## Compare grabbed and expected image and get result of comparison
                    video_result1 = NOS_API.compare_pictures("HDMI_video_ref1", "HDMI_video", "[HALF_SCREEN]")
                    video_result2 = NOS_API.compare_pictures("HDMI_video_ref2", "HDMI_video", "[HALF_SCREEN]")
                    video_result3 = NOS_API.compare_pictures("HDMI_video_ref3", "HDMI_video", "[HALF_SCREEN]")
                    video_result4 = NOS_API.compare_pictures("HDMI_video_ref4", "HDMI_video", "[HALF_SCREEN]")
                except Exception as error:
                    ## Set test result to INCONCLUSIVE
                    TEST_CREATION_API.write_log_to_file(str(error))
                    NOS_API.set_error_message("Video HDMI")
                    test_result = "FAIL"
                    TEST_CREATION_API.write_log_to_file("There is no signal on HDMI 720p interface.")
            
                ## Check video analysis results and update comments
                if (video_result1 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result2 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result3 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result4 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                    ## Set test result to PASS
                    test_result_quality = True
                else:
                    TEST_CREATION_API.write_log_to_file("Video with RT-RK pattern is not reproduced correctly on HDMI 720p.")
                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                    + "; V: " + str(video_result))
                    NOS_API.set_error_message("Video HDMI")
                    error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                    error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message
                
        ###################################################### 720p HDMI Audio ######################################################### 
            
            if(test_result_quality):
        
                ## Record audio from digital output (HDMI)
                time.sleep(0.5)
                TEST_CREATION_API.record_audio("HDMI_audio_720", MAX_RECORD_AUDIO_TIME)

                ## Compare recorded and expected audio and get result of comparison
                audio_result_1 = NOS_API.compare_audio("No_Both_ref", "HDMI_audio_720")

                if not(audio_result_1 < TEST_CREATION_API.AUDIO_THRESHOLD):
                    
                    TEST_CREATION_API.send_ir_rc_command("[CH+]")
                    TEST_CREATION_API.send_ir_rc_command("[CH-]")
                    time.sleep(NOS_API.MAX_ZAP_TIME)
                    ## Record audio from digital output (HDMI)
                    TEST_CREATION_API.record_audio("HDMI_audio_720_1", MAX_RECORD_AUDIO_TIME)
        
                    ## Compare recorded and expected audio and get result of comparison
                    audio_result_1 = NOS_API.compare_audio("No_Both_ref", "HDMI_audio_720_1")
        
                if not(audio_result_1 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                    HDMI_Result = True                                                         
                else:
                    try:
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                    except: 
                        pass
                        
                    NOS_API.Inspection = True
                    
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
                        time.sleep(15)
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
                    
                    NOS_API.initialize_grabber()
                    
                    ## Start grabber device with video on default video source
                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                    TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.HDMI1)
                    time.sleep(2)
                    
                    TEST_CREATION_API.record_audio("HDMI_audio_720_2", MAX_RECORD_AUDIO_TIME)

                    ## Compare recorded and expected audio and get result of comparison
                    audio_result_1 = NOS_API.compare_audio("No_Both_ref", "HDMI_audio_720_2")

                    if(audio_result_1 < TEST_CREATION_API.AUDIO_THRESHOLD):
                        HDMI_Result = True 
                    else:
                        TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on hdmi 720p interface.")
                        NOS_API.set_error_message("Audio HDMI")
                        NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_code  \
                                                                + ";\n" + NOS_API.test_cases_results_info.hdmi_720p_signal_interference_error_code  \
                                                                + "; Error messages: " + NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_message \
                                                                + ";\n" + NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_message)
                        error_codes = NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.hdmi_720p_signal_interference_error_code
                        error_messages = NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_message + " " + NOS_API.test_cases_results_info.hdmi_720p_signal_interference_error_message

                        ############################################# SCART Test ###################################################################################
                   
                if(HDMI_Result):
                    NOS_API.grabber_stop_video_source()
                    time.sleep(1)
                    NOS_API.grabber_stop_audio_source()
                    time.sleep(1)
                    
                    ## Initialize input interfaces of DUT RT-AV101 device 
                    NOS_API.reset_dut()
                    
                    ## Start grabber device with video on SCART video source
                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                    time.sleep(WAIT_TO_SWITCH_SCART)
                              
                    # Zap to service
                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")

                    time.sleep(6)
                    
                    if not(NOS_API.is_video_playing(TEST_CREATION_API.VideoInterface.CVBS2)):
                        
                        NOS_API.display_dialog("Confirme o cabo SCART e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                        time.sleep(2)
                    
                    ## Check if video is playing (check if video is not freezed)
                    if (NOS_API.is_video_playing(TEST_CREATION_API.VideoInterface.CVBS2)):
                        video_result = 0

                        try:
                           ## Perform grab picture
                            try:
                                TEST_CREATION_API.grab_picture("SCART_video")
                            except: 
                                time.sleep(5)
                                try:
                                    TEST_CREATION_API.grab_picture("SCART_video")
                                except:
                                    
                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video SCART")
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

                            ## Compare grabbed and expected image and get result of comparison
                            video_result1 = NOS_API.compare_pictures("SCART_video_ref1", "SCART_video", "[HALF_SCREEN_576p]")
                            video_result2 = NOS_API.compare_pictures("SCART_video_ref2", "SCART_video", "[HALF_SCREEN_576p]")
                            video_result3 = NOS_API.compare_pictures("SCART_video_ref3", "SCART_video", "[HALF_SCREEN_576p]")
                           
                        except Exception as error:
                           ## Set test result to INCONCLUSIVE
                           TEST_CREATION_API.write_log_to_file(str(error))
                           test_result = "FAIL"
                           TEST_CREATION_API.write_log_to_file("There is no signal on SCART interface.")
                           NOS_API.set_error_message("Video Scart")

                        ## Check video analysis results and update comments
                        if (video_result1 >= NOS_API.DEFAULT_CVBS_VIDEO_THRESHOLD or video_result2 >= NOS_API.DEFAULT_CVBS_VIDEO_THRESHOLD or video_result3 >= NOS_API.DEFAULT_CVBS_VIDEO_THRESHOLD):
                           ## Set test result to PASS
                           test_result_SCART_video = True
                        else:
                            TEST_CREATION_API.write_log_to_file("Video with RT-RK pattern is not reproduced correctly on SCART interface.")
                            NOS_API.set_error_message("Video Scart")
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_noise_error_code \
                                                               + "; Error message: " + NOS_API.test_cases_results_info.scart_noise_error_message \
                                                               + "; V: " + str(video_result))
                            error_codes = NOS_API.test_cases_results_info.scart_noise_error_code
                            error_messages =  NOS_API.test_cases_results_info.scart_noise_error_message

                    else:
                        TEST_CREATION_API.write_log_to_file("Channel with RT-RK color bar pattern was not playing on SCART interface.")
                        NOS_API.set_error_message("Video Scart")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                                               + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message \
                                                               + "; Video is not playing on SCART interface")
                        error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                        error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message

                    ######################################################## SCART Audio ##################################################################
                    
                    if(test_result_SCART_video):
                    
                        NOS_API.grabber_stop_video_source()
                        time.sleep(0.5)
                    
                        ## Start grabber device with audio on SCART audio source
                        TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.LINEIN2)
                        time.sleep(3)
                
                        ## Record audio from digital output (SCART)
                        TEST_CREATION_API.record_audio("SCART_audio", MAX_RECORD_AUDIO_TIME)

                        ## Compare recorded and expected audio and get result of comparison
                        audio_result_1 = NOS_API.compare_audio("No_Left_ref", "SCART_audio")
                        audio_result_2 = NOS_API.compare_audio("No_Right_ref", "SCART_audio")
                        audio_result_3 = NOS_API.compare_audio("No_Both_ref", "SCART_audio")
                        
                        if not(audio_result_1 < TEST_CREATION_API.AUDIO_THRESHOLD and audio_result_2 < TEST_CREATION_API.AUDIO_THRESHOLD and audio_result_3 < TEST_CREATION_API.AUDIO_THRESHOLD):
                           
                            NOS_API.display_dialog("Confirme o cabo SCART e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                            
                            ## Record audio from digital output (SCART)
                            TEST_CREATION_API.record_audio("SCART_audio_1", MAX_RECORD_AUDIO_TIME)
                    
                            ## Compare recorded and expected audio and get result of comparison
                            audio_result_1 = NOS_API.compare_audio("No_Left_ref", "SCART_audio_1")
                            audio_result_2 = NOS_API.compare_audio("No_Right_ref", "SCART_audio_1")
                            audio_result_3 = NOS_API.compare_audio("No_Both_ref", "SCART_audio_1")
                            
                            if not(audio_result_1 < TEST_CREATION_API.AUDIO_THRESHOLD and audio_result_2 < TEST_CREATION_API.AUDIO_THRESHOLD and audio_result_3 < TEST_CREATION_API.AUDIO_THRESHOLD):
                                
                                try:
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                except: 
                                    pass
                                    
                                NOS_API.Inspection = True
                                
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
                                    time.sleep(15)
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
                                
                                NOS_API.initialize_grabber()
                                
                                ## Start grabber device with audio on SCART audio source
                                TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.LINEIN2)
                                time.sleep(3)
                                
                                ## Record audio from digital output (SCART)
                                TEST_CREATION_API.record_audio("SCART_audio_2", MAX_RECORD_AUDIO_TIME)
                            
                                ## Compare recorded and expected audio and get result of comparison
                                audio_result_1 = NOS_API.compare_audio("No_Left_ref", "SCART_audio_2")
                                audio_result_2 = NOS_API.compare_audio("No_Right_ref", "SCART_audio_2")
                                audio_result_3 = NOS_API.compare_audio("No_Both_ref", "SCART_audio_2")
                        
                        if (audio_result_1 < TEST_CREATION_API.AUDIO_THRESHOLD and audio_result_2 < TEST_CREATION_API.AUDIO_THRESHOLD and audio_result_3 < TEST_CREATION_API.AUDIO_THRESHOLD):
                            #test_result = "PASS"
                            SCART_Result = True         
                        else:
                            TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on SCART interface.")
                            NOS_API.set_error_message("Audio Scart")
                            NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.scart_signal_discontinuities_error_code  \
                                                                    + ";\n" + NOS_API.test_cases_results_info.scart_signal_interference_error_code  \
                                                                    + "; Error messages: " + NOS_API.test_cases_results_info.scart_signal_discontinuities_error_message \
                                                                    + ";\n" + NOS_API.test_cases_results_info.scart_signal_discontinuities_error_message)
                            error_codes = NOS_API.test_cases_results_info.scart_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.scart_signal_interference_error_code
                            error_messages = NOS_API.test_cases_results_info.scart_signal_discontinuities_error_message + " " + NOS_API.test_cases_results_info.scart_signal_interference_error_message
            
       ####################################################################### SPDIF Test ####################################################################
                    
                        if(SCART_Result):
                            
                            NOS_API.grabber_stop_audio_source()
                            time.sleep(0.5)
                            ## Start grabber device with audio on SPDIF Coaxial source
                            TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.SPDIF_COAX)

                            ## Zap to service
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")

                            ## Set volume to max
                            TEST_CREATION_API.send_ir_rc_command("[VOL_MAX]")

                            ## Record audio from digital output (SPDIF COAX)
                            TEST_CREATION_API.record_audio("SPDIF_COAX_audio", MAX_RECORD_AUDIO_TIME)

                            ## Compare recorded and expected audio and get result of comparison
                            audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_COAX_audio")        
                            
                            if not(audio_result1 < TEST_CREATION_API.AUDIO_THRESHOLD):
                            
                                NOS_API.display_dialog("Confirme o cabo SPDIF e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                            
                                ## Record audio from digital output (SPDIF COAX)
                                TEST_CREATION_API.record_audio("SPDIF_COAX_audio_1", MAX_RECORD_AUDIO_TIME)
                        
                                ## Compare recorded and expected audio and get result of comparison
                                audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_COAX_audio_1")
                                
                                if not(audio_result1 < TEST_CREATION_API.AUDIO_THRESHOLD):
                                
                                    try:
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                    except: 
                                        pass
                                        
                                    NOS_API.Inspection = True
                                    
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
                                        time.sleep(15)
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
                                    
                                    NOS_API.initialize_grabber()
                                    
                                    TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.SPDIF_COAX)
                                    time.sleep(1)
                                        
                                    ## Record audio from digital output (SPDIF COAX)
                                    TEST_CREATION_API.record_audio("SPDIF_COAX_audio_2", MAX_RECORD_AUDIO_TIME)
                                
                                    ## Compare recorded and expected audio and get result of comparison
                                    audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_COAX_audio_2")
                            
                            if not(audio_result1 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                                test_result_SPDIF_COAX = True
                            else:
                                TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on SPDIF coaxial interface.")
                                NOS_API.set_error_message("SPDIF")
                                NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_code  \
                                                                           + ";\n" + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_code  \
                                                                           + "; Error messages: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_message \
                                                                           + ";\n" + NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_message)
                                error_codes = NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_code
                                error_messages = NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_message + " " + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_message
    
                            ####################################################SPDIF OPT Audio################################################################## 

                            if(test_result_SPDIF_COAX):
                            
                                NOS_API.grabber_stop_audio_source()
                                time.sleep(0.5)
                                
                                ## Start grabber device with audio on default audio source
                                TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.SPDIF_OPT)
                        
                                ## Zap to service
                                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            
                                ## Set volume to max
                                TEST_CREATION_API.send_ir_rc_command("[VOL_MAX]")
                        
                                ## Record audio from digital output (SPDIF OPT)
                                TEST_CREATION_API.record_audio("SPDIF_OPT_audio", MAX_RECORD_AUDIO_TIME)
                        
                                ## Compare recorded and expected audio and get result of comparison
                                audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_OPT_audio")
                                
                                if not(audio_result1 < TEST_CREATION_API.AUDIO_THRESHOLD):
                                    
                                    NOS_API.display_dialog("Confirme o cabo TOSLINK e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                                    
                                    ## Record audio from digital output (SPDIF OPT)
                                    TEST_CREATION_API.record_audio("SPDIF_OPT_audio_1", MAX_RECORD_AUDIO_TIME)
                        
                                    ## Compare recorded and expected audio and get result of comparison
                                    audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_OPT_audio_1")
                                    
                                    if not(audio_result1 < TEST_CREATION_API.AUDIO_THRESHOLD):
                                    
                                        try:
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                        except: 
                                            pass
                                            
                                        NOS_API.Inspection = True
                                        
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
                                            time.sleep(15)
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
                                        
                                        NOS_API.initialize_grabber()
                                        
                                        ## Start grabber device with audio on default audio source
                                        TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.SPDIF_OPT)
                                        time.sleep(1)
                                    
                                        ## Record audio from digital output (SPDIF OPT)
                                        TEST_CREATION_API.record_audio("SPDIF_OPT_audio_2", MAX_RECORD_AUDIO_TIME)
                                    
                                        ## Compare recorded and expected audio and get result of comparison
                                        audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_OPT_audio_2")
                        
                                if not(audio_result1 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                                    #test_result = "PASS"
                                    SPDIF_Result = True                            
                                else:
                                    TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on SPDIF optical interface.")
                                    NOS_API.set_error_message("TOSLINK")
                                    NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.spdif_optical_signal_discontinuities_error_code  \
                                                                            + ";\n" + NOS_API.test_cases_results_info.spdif_optical_signal_interference_error_code  \
                                                                            + "; Error messages: " + NOS_API.test_cases_results_info.spdif_optical_signal_discontinuities_error_message \
                                                                            + ";\n" + NOS_API.test_cases_results_info.spdif_optical_signal_discontinuities_error_message)
                                    error_codes = NOS_API.test_cases_results_info.spdif_optical_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.spdif_optical_signal_interference_error_code
                                    error_messages = NOS_API.test_cases_results_info.spdif_optical_signal_discontinuities_error_message + " " + NOS_API.test_cases_results_info.spdif_optical_signal_interference_error_message

     #################################################################### Telnet #########################################################################    
                                            
                                if(SPDIF_Result):                        
                                    cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode
                                    #Get start time
                                    startTime = time.localtime()
                                    sid = NOS_API.get_session_id()
                                    while (True):
                                        
                                        response = NOS_API.send_cmd_to_telnet(sid, cmd)
                                        TEST_CREATION_API.write_log_to_file("response:" + str(response))
                                        if(response != None):
                                            
                                            if(response.find("Error:") != -1):
                                                error_command_telnet = True
                                                break
                                            if(response != "BUSY"):
                                                stb_state = NOS_API.is_stb_operational(response)
                                                break
                                        else:
                                            NOS_API.set_error_message("Telnet timeout")
                                            TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                            
                                            error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                            error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                
                                            NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
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
                                            NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)  
                                            return
                                            
                                        time.sleep(5)
                                            
                                        #Get current time
                                        currentTime = time.localtime()
                                        if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                                            NOS_API.set_error_message("Telnet timeout")
                                            TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                            
                                            error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                            error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
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
                                            NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)  
                                            return
                                    
                                    if(error_command_telnet == False):
                                        if(stb_state == True):
                                        
                                            cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode + ' verbose'
                                            startTime = time.localtime()
                                            while (True):
                                        
                                                response = NOS_API.send_cmd_to_telnet(sid, cmd)
                                                TEST_CREATION_API.write_log_to_file("response:" + str(response))                
                                                
                                                if(response != None and response != "BUSY"):
                                                    data = NOS_API.parse_telnet_cmd1(response)
                                                    break
                                                if(response == None):
                                                    NOS_API.set_error_message("Telnet timeout")
                                                    TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                                    
                                                    error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                    error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                        
                                                    NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
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
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)  
                                                    return
                                                    
                                                time.sleep(5)
                                                    
                                                #Get current time
                                                currentTime = time.localtime()
                                                if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                                                    NOS_API.set_error_message("Telnet timeout")
                                                    TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                                    
                                                    error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                    error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                        
                                                    NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
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
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)  
                                                    return
                                                    
                                                                                                
                                                
                                            if (data[1] == "Operational"):
                                                NOS_API.test_cases_results_info.ip = data[0]
                                                test_result = "PASS"
                                            else:           
                                                TEST_CREATION_API.write_log_to_file("STB State is not operational")
                                                NOS_API.set_error_message("CM Docsis")
                                                error_codes = NOS_API.test_cases_results_info.ip_error_code
                                                error_messages = NOS_API.test_cases_results_info.ip_error_message  
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.ip_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.ip_error_message)
                                        else:
                                            TEST_CREATION_API.write_log_to_file("STB State is not operational")
                                            NOS_API.set_error_message("CM Docsis")
                                            error_codes = NOS_API.test_cases_results_info.ip_error_code
                                            error_messages = NOS_API.test_cases_results_info.ip_error_message  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.ip_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.ip_error_message)
                                    else:
                                        NOS_API.set_error_message("Telnet timeout")
                                        TEST_CREATION_API.write_log_to_file("Error on Telnet communication")
                                        
                                        error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                        error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                                                
                                    NOS_API.quit_session(sid)
                                                        
            System_Failure = 2
        ################################################################################################################################
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
