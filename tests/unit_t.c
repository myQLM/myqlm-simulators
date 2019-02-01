/* -*- coding: utf-8 -*-
 ###############################################################################
 # Author: Pierre Vigneras <pierre.vigneras@bull.net>
 # Created on: May 21, 2013
 # Contributors:
 ###############################################################################
 # Copyright (C) 2012  Bull S. A. S.  -  All rights reserved
 # Bull, Rue Jean Jaures, B.P.68, 78340, Les Clayes-sous-Bois
 # This is not Free or Open Source software.
 # Please contact Bull S. A. S. for details about its license.
 ###############################################################################
 */

#include <CUnit/Basic.h>
#include <CUnit/Console.h>
#include <CUnit/Automated.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdbool.h>
#include <stddef.h>
#include <libgen.h>
#include <fcntl.h>

#include <sched.h>

#include <linux/limits.h>

#define UNUSED(x) (void)(x)

void test_func(){
    CU_ASSERT_TRUE(false);
}


// Actual test functions are separated into their respective test file.
// However, to prevent defining related .h, we define all functions here

/* Test if the test have been run correctly */
int _handle_rc_code(){
    if(CU_get_error()!=0){
        return 99;
    } else {
        fprintf(stderr, "CU_get_number_of_suites_failed %d, "
                "CU_get_number_of_tests_failed %d, "
                "CU_get_number_of_failures %d\n",
                CU_get_number_of_suites_failed(),
                CU_get_number_of_tests_failed(),
                CU_get_number_of_failures());
        if(CU_get_number_of_failures() != 0){
            return 1;
        }
    }
    return 0;
}


/* The main() function for setting up and running the tests.
 * Returns a CUE_SUCCESS on successful running, another
 * CUnit error code on failure.
 */
int main(int argc, char * argv[]) {
    UNUSED(argc);
    UNUSED(argv);

    /* initialize the CUnit test registry */
    if (CUE_SUCCESS != CU_initialize_registry()) return CU_get_error();


    /* add suites to the registry */
    CU_pSuite test_suite = CU_add_suite("test_suite", NULL, NULL);
    if (NULL == test_suite) {
        CU_cleanup_registry();
        return (CU_get_error());
    }

    /* add the tests to the suite */
    if (false
        || (NULL == CU_add_test(test_suite, "test function unitary", test_func))
        || false) {
        CU_cleanup_registry();
        return (CU_get_error());
    }



    /* Run all tests using the automated interface */
    CU_set_output_filename("./report/cunit");
    CU_automated_run_tests();
    CU_list_tests_to_file();

    int rc = _handle_rc_code();

    /* Run all tests using the CUnit Basic interface */
    CU_basic_set_mode(CU_BRM_VERBOSE);
    CU_basic_run_tests();
    printf("\n");
    CU_basic_show_failures(CU_get_failure_list());
    printf("\n\n");

    int rc2 = _handle_rc_code();
    rc = rc > rc2 ? rc : rc2;

    CU_cleanup_registry();


    return rc;
}
