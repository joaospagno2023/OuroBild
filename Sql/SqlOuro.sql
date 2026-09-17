--select * from PipelineExecutions

--select * from ApplicationConfiguration

select * from PipelineExecutionLogs ORDER BY Id desc

truncate table PipelineExecutionLogs

delete from  PipelineExecutions



--select * from SetupPublicationLogs


select * from CleanupRules



select a.projectid,* from Projects a order by a.projectid desc 

select * from ProjectSourceStates