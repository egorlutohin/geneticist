SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE `patient_fullhistoricalpatient` ADD COLUMN `added_by` integer NOT NULL DEFAULT 1;
CREATE INDEX `patient_fullhistoricalpatient_599dcce2` ON `patient_fullhistoricalpatient` (`type`);
ALTER TABLE `patient_fullhistoricaldiagnosis` ADD COLUMN `date_created` datetime NOT NULL DEFAULT '1900-01-01 00:00:00';
ALTER TABLE `patient_diagnosis` ADD COLUMN `date_created` datetime NOT NULL DEFAULT '1900-01-01 00:00:00';
ALTER TABLE `patient_patient` ADD COLUMN `added_by` integer NOT NULL DEFAULT 1;
CREATE INDEX `patient_patient_599dcce2` ON `patient_patient` (`type`);
SET FOREIGN_KEY_CHECKS=1;
