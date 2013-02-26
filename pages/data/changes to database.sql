-- Additional columns to fiscal_data table
-- id - primary key INT
-- changed_by STRING - who edited the record
-- change_date DATETIME - when it was edited
-- action (create | update | delete| comment | review) STRING - what was done with the record
-- status SET(pending,  approved, rejected ) - to be changed by "moderator"




ALTER TABLE fiscal_data
  ADD COLUMN changed_by VARCHAR(255) NULL
, ADD COLUMN change_date DATETIME NULL
, ADD COLUMN status VARCHAR(45) NULL
, ADD COLUMN action VARCHAR(45) NULL
, ADD COLUMN id INT NOT NULL AUTO_INCREMENT

, ADD PRIMARY KEY (id)
, ADD UNIQUE INDEX id_UNIQUE (id ASC)
, ADD iso_INDEX (iso ASC)
, DROP INDEX countryname
;

ALTER TABLE `fiscal_data` MODIFY COLUMN `change_date` TIMESTAMP NOT
NULL DEFAULT CURRENT_TIMESTAMP;

-- ????
ALTER TABLE fiscal_data ENGINE=`InnoDB`;

-- change to fiscal_data
-- new column action
-- not null values
ALTER TABLE `fiscal_data` CHANGE COLUMN `iso` `iso` CHAR(3) NULL  ,
 CHANGE COLUMN `currency` `currency` VARCHAR(12) NULL  ,
 CHANGE COLUMN `year` `year` INT(4) NULL  ,
 CHANGE COLUMN `debt_exports` `debt_exports` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `public_plus_private_debt_gdp` `public_plus_private_debt_gdp` DECIMAL(6,4) NULL  ,
 CHANGE COLUMN `domestic_plus_external_debt_gdp` `domestic_plus_external_debt_gdp` DECIMAL(6,4) NULL  ,
 CHANGE COLUMN `debt_gnp` `debt_gnp` DECIMAL(6,4) NULL  ,
 CHANGE COLUMN `currency_crisis` `currency_crisis` INT(1) NULL  ,
 CHANGE COLUMN `inflation_crisis` `inflation_crisis` INT(1) NULL  ,
 CHANGE COLUMN `stock_market_crash` `stock_market_crash` INT(1) NULL  ,
 CHANGE COLUMN `soverign_debt_crisis_domestic` `soverign_debt_crisis_domestic` INT(1) NULL  ,
 CHANGE COLUMN `sovereign_debt_crisis_external` `sovereign_debt_crisis_external` INT(1) NULL  ,
 CHANGE COLUMN `banking_crisis` `banking_crisis` INT(1) NULL  ,
 CHANGE COLUMN `crisis_tally` `crisis_tally` INT(1) NULL  ,
 CHANGE COLUMN `gov_revenue` `gov_revenue` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `gov_spending` `gov_spending` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `gov_debt` `gov_debt` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `int_on_gov_debt` `int_on_gov_debt` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `Short_term_interest_rate` `Short_term_interest_rate` DECIMAL(4,2) NULL  ,
 CHANGE COLUMN `gdp` `gdp` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `gov_bond_yield` `gov_bond_yield` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `price_index` `price_index` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `int_revenue` `int_revenue` DECIMAL(6,4) NULL  ,
 CHANGE COLUMN `outstanding_bond` `outstanding_bond` DOUBLE NULL  ,
 CHANGE COLUMN `avg_maturity` `avg_maturity` DOUBLE NULL  ,
 CHANGE COLUMN `int_expense_general` `int_expense_general` DOUBLE NULL  ,
 CHANGE COLUMN `gov_revenue_general` `gov_revenue_general` DOUBLE NULL  ,
 CHANGE COLUMN `gov_spending_general` `gov_spending_general` DOUBLE NULL  ,
 CHANGE COLUMN `source` `source` TEXT NULL  ,
 CHANGE COLUMN `income_tax_revenue` `income_tax_revenue` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `consumption_tax_revenue` `consumption_tax_revenue` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `military_spending` `military_spending` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `social_insurance_spending` `social_insurance_spending` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `health_expenditure` `health_expenditure` DOUBLE(25,2) NULL  ,
 CHANGE COLUMN `comments` `comments` TEXT NULL  ,
 CHANGE COLUMN `user_comment` `user_comment` LONGTEXT NULL  ,
 CHANGE COLUMN `domestic_debt` `domestic_debt` DOUBLE(18,2) NULL  ,
 CHANGE COLUMN `foreign_debt` `foreign_debt` DOUBLE(18,2) NULL  ,
 CHANGE COLUMN `changed_by` `changed_by` VARCHAR(255) NULL  ,
 CHANGE COLUMN `change_date` `change_date` DATETIME NULL  ,
 CHANGE COLUMN `status` `status` VARCHAR(45) NULL  ,
 DROP INDEX `countryname` ;


-- TODO: remove not null restrictions from fiscal_data table


-- fiscal_data_log
-- Contains changes to fiscal_data.
-- Has the same fields plus:
--
-- verified_by  - who verified the record
-- verification_date DATETIME - when the record was verified
-- active (yes | no ) STRING - if 'yes'  fiscal_data has the same record. Changed by "moderator".
-- log_id -  INT - primary key

-- create  fiscal_data_log and copy data from fiscal_data
DROP TABLE IF EXISTS  fiscal_data_log;
CREATE TABLE fiscal_data_log LIKE fiscal_data;
INSERT INTO fiscal_data_log SELECT * FROM fiscal_data;

-- ADD additional fields and make a primary key
ALTER TABLE fiscal_data_log
  CHANGE COLUMN id id INT(11) NULL
, ADD COLUMN active VARCHAR(45) NULL
, ADD COLUMN verified_by VARCHAR(255) NULL
, ADD COLUMN verification_date DATETIME NULL
, ADD COLUMN log_id INT NOT NULL AUTO_INCREMENT
, DROP PRIMARY KEY
, ADD PRIMARY KEY (log_id)
, ADD UNIQUE INDEX log_id_UNIQUE (log_id ASC)
, DROP INDEX id_UNIQUE
, ADD INDEX id_INDEX (id ASC)
, ADD INDEX change_date_INDEX (change_date ASC)
;


ALTER TABLE `fiscal_data_log` MODIFY COLUMN `change_date` TIMESTAMP NOT
NULL DEFAULT CURRENT_TIMESTAMP;

-- ????
ALTER TABLE fiscal_data_log ENGINE=`InnoDB`;

-- before update trigger on fiscal_data

DROP TRIGGER IF EXISTS fiscal_data_on_before_update;

delimiter //
CREATE TRIGGER fiscal_data_on_before_update BEFORE UPDATE ON fiscal_data
  FOR EACH ROW
    IF @disable_triggers IS NULL THEN
      row_block: BEGIN

         -- if the client did not set action, assume it is 'update'
          IF NEW.action is NULL THEN
             SET NEW.action = 'update';
          END IF;


          -- prevent copying into _log if this is verification
           IF  (NEW.action = 'verify')
		   THEN
				SET NEW.action = 'verified';
                SET NEW.change_date = NOW();
				LEAVE row_block;
           END IF;

          -- set all records in _log as not active
          UPDATE fiscal_data_log
          SET fiscal_data_log.active='no'
          WHERE fiscal_data_log.id=NEW.id;

          -- create a new record in _log and set it active
          SET NEW.change_date = NOW();
          -- SET NEW.change_date = TIMESTAMP(NOW(), '00:00:01');
          SET NEW.status = 'pending';


          INSERT INTO fiscal_data_log
            (
            iso,
            currency,
            year,
            debt_exports,
            public_plus_private_debt_gdp,
            domestic_plus_external_debt_gdp,
            debt_gnp,
            currency_crisis,
            inflation_crisis,
            stock_market_crash,
            soverign_debt_crisis_domestic,
            sovereign_debt_crisis_external,
            banking_crisis,
            crisis_tally,
            gov_revenue,
            gov_spending,
            gov_debt,
            int_on_gov_debt,
            Short_term_interest_rate,
            gdp,
            gov_bond_yield,
            price_index,
            int_revenue,
            outstanding_bond,
            avg_maturity,
            int_expense_general,
            gov_revenue_general,
            gov_spending_general,
            source,
            income_tax_revenue,
            consumption_tax_revenue,
            military_spending,
            social_insurance_spending,
            health_expenditure,
            comments,
            user_comment,
            domestic_debt,
            foreign_debt,
            id,
            changed_by,
            change_date,
            status,
            action,
            active
          )
          VALUES
          (
            NEW.iso,
            NEW.currency,
            NEW.year,
            NEW.debt_exports,
            NEW.public_plus_private_debt_gdp,
            NEW.domestic_plus_external_debt_gdp,
            NEW.debt_gnp,
            NEW.currency_crisis,
            NEW.inflation_crisis,
            NEW.stock_market_crash,
            NEW.soverign_debt_crisis_domestic,
            NEW.sovereign_debt_crisis_external,
            NEW.banking_crisis,
            NEW.crisis_tally,
            NEW.gov_revenue,
            NEW.gov_spending,
            NEW.gov_debt,
            NEW.int_on_gov_debt,
            NEW.Short_term_interest_rate,
            NEW.gdp,
            NEW.gov_bond_yield,
            NEW.price_index,
            NEW.int_revenue,
            NEW.outstanding_bond,
            NEW.avg_maturity,
            NEW.int_expense_general,
            NEW.gov_revenue_general,
            NEW.gov_spending_general,
            NEW.source,
            NEW.income_tax_revenue,
            NEW.consumption_tax_revenue,
            NEW.military_spending,
            NEW.social_insurance_spending,
            NEW.health_expenditure,
            NEW.comments,
            NEW.user_comment,
            NEW.domestic_debt,
            NEW.foreign_debt,
            NEW.id,
            NEW.changed_by,
            NEW.change_date,
            NEW.status,
            NEW.action,
            'yes'
          );

      END row_block;
    END IF;

//
delimiter ;


-- Countries

CREATE TABLE `countries2` (
       `iso` char(3) NOT NULL,
       `country` varchar(50) DEFAULT NULL,
       `current_currency` char(3) DEFAULT NULL,
       PRIMARY KEY (`iso`)
     ) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
     ;
INSERT INTO countries2 SELECT * FROM countries;
rename table countries to countries_old;
rename table countries2 to countries;


CREATE TABLE users_roles (
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  role varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (id),
  KEY name_role_index (name,role)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
