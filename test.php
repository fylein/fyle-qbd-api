<?php
if($is_executed_from_cron){
    $employee_status = $uknowvauser->getInfo('EMPLOYMENTSTATUS_EMPINFO');
    $month = date('m');
    $year_start = HRMHelper::getParam('year_start');
    
    // For Probation and Trainee employees, always allocate 0.5 leaves per month
    if($employee_status == 'Probation' || $employee_status == 'Trainee'){
        $leavenumber = 0.5;
    }
    // For Confirmed employees, handle the complex allocation logic
    else if($employee_status == 'Confirmed'){
        $doc = $uknowvauser->getInfo('CONFIRMATIONDATE_SALARYINFO');
        $conf_year_month = date('Y-m',strtotime($doc));
        $conf_month = date('m',strtotime($doc));
        $average_leave = $leavetype->allowed_leaves/12;
        
        if($year_start <= $conf_month){
            $start_year = $year_start - 1;
            $finance_month = $conf_month - $start_year;
            $pending_month = 12 - $finance_month;
            $pending_leave = $pending_month * $average_leave;
        }else{
            $start_year = $year_start - 1;
            $finance_month = $start_year - $conf_month;
            $pending_leave = $finance_month * $average_leave;
        }
        
        $last_year_month = date("Y-m",strtotime("-1 month"));
        
        if($month == $year_start){
            // At financial year start, give full annual allocation
            $leavenumber = $leavetype->allowed_leaves;
        }else{
            // For other months, give pending leave only in confirmation month
            if($last_year_month == $conf_year_month){
                $leavenumber = $pending_leave;
            }else{
                $leavenumber = 0;
            }
        }
    }
}else{ 
    $doj = HrmHelper::getDateOfJoining($uknowvauser->id);
    $doj_day = date('d',strtotime($doj));
    $employee_status = $uknowvauser->getInfo('EMPLOYMENTSTATUS_EMPINFO');
    $maxDays = date('t');

    // For new joiners who are Probation/Trainee
    if($employee_status == 'Probation' || $employee_status == 'Trainee'){
        if($doj_day <= 15){
            $leavenumber = 0.5;
        }else{
            $leavenumber = 0;
        }
    }
    // For new joiners who are Confirmed, calculate prorated leaves
    else if($employee_status == 'Confirmed'){
        $average_leave = $leavetype->allowed_leaves/12;
        if($doj_day <= 15){
            $leavenumber = $average_leave;
        }else{
            $leavenumber = 0;
        }
    }
}
?>