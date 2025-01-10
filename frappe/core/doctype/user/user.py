# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from collections.abc import Iterable
from datetime import timedelta

import frappe
import frappe.defaults
import frappe.permissions
import frappe.share
from frappe import STANDARD_USERS, _, msgprint, throw
from frappe.apps import get_default_path
from frappe.auth import MAX_PASSWORD_SIZE
from frappe.core.doctype.user_type.user_type import user_linked_with_permission_on_doctype
from frappe.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
	toggle_notifications,
)
from frappe.desk.notifications import clear_notifications
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.rate_limiter import rate_limit
from frappe.utils import (
	cint,
	escape_html,
	flt,
	format_datetime,
	get_formatted_email,
	get_system_timezone,
	has_gravatar,
	now_datetime,
	today,
)
from frappe.utils.data import sha256_hash
from frappe.utils.password import check_password, get_password_reset_limit
from frappe.utils.password import update_password as _update_password
from frappe.utils.user import get_system_managers
from frappe.website.utils import get_home_page, is_signup_disabled

desk_properties = (
	"search_bar",
	"notifications",
	"list_sidebar",
	"bulk_actions",
	"view_switcher",
	"form_sidebar",
	"timeline",
	"dashboard",
)


class User(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.core.doctype.block_module.block_module import BlockModule
		from frappe.core.doctype.defaultvalue.defaultvalue import DefaultValue
		from frappe.core.doctype.has_role.has_role import HasRole
		from frappe.core.doctype.user_email.user_email import UserEmail
		from frappe.core.doctype.user_role_profile.user_role_profile import UserRoleProfile
		from frappe.core.doctype.user_social_login.user_social_login import UserSocialLogin
		from frappe.types import DF

		allowed_in_mentions: DF.Check
		api_key: DF.Data | None
		api_secret: DF.Password | None
		banner_image: DF.AttachImage | None
		bio: DF.SmallText | None
		birth_date: DF.Date | None
		block_modules: DF.Table[BlockModule]
		bulk_actions: DF.Check
		bypass_restrict_ip_check_if_2fa_enabled: DF.Check
		code_editor_type: DF.Literal["vscode", "vim", "emacs"]
		concentration: DF.Data | None
		crunchbase: DF.Data | None
		dashboard: DF.Check
		default_app: DF.Literal[None]
		default_workspace: DF.Link | None
		defaults: DF.Table[DefaultValue]
		desk_theme: DF.Literal["Light", "Dark", "Automatic"]
		document_follow_frequency: DF.Literal["Hourly", "Daily", "Weekly"]
		document_follow_notify: DF.Check
		email: DF.Data
		email_signature: DF.TextEditor | None
		enabled: DF.Check
		first_name: DF.Data
		follow_assigned_documents: DF.Check
		follow_commented_documents: DF.Check
		follow_created_documents: DF.Check
		follow_liked_documents: DF.Check
		follow_shared_documents: DF.Check
		form_sidebar: DF.Check
		full_name: DF.Data | None
		gender: DF.Link | None
		home_settings: DF.Code | None
		instagram: DF.Data | None
		interest: DF.SmallText | None
		language: DF.Link | None
		last_active: DF.Datetime | None
		last_ip: DF.ReadOnly | None
		last_known_versions: DF.Text | None
		last_login: DF.ReadOnly | None
		last_name: DF.Data
		last_password_reset_date: DF.Date | None
		last_reset_password_key_generated_on: DF.Datetime | None
		linkedin_1: DF.Data | None
		list_sidebar: DF.Check
		location: DF.Data | None
		login_after: DF.Int
		login_before: DF.Int
		logout_all_sessions: DF.Check
		major: DF.Data
		membership: DF.Literal["0 - None", "1 - Student", "2 - Member", "3 - Scholar", "4 - Administrative"]
		middle_name: DF.Data | None
		mobile_no: DF.Data | None
		module_profile: DF.Link | None
		mute_sounds: DF.Check
		new_password: DF.Password | None
		notifications: DF.Check
		onboarding_status: DF.SmallText | None
		phone: DF.Data | None
		program: DF.Data | None
		redirect_url: DF.SmallText | None
		reset_password_key: DF.Data | None
		restrict_ip: DF.SmallText | None
		role_profile_name: DF.Link | None
		role_profiles: DF.TableMultiSelect[UserRoleProfile]
		roles: DF.Table[HasRole]
		search_bar: DF.Check
		send_me_a_copy: DF.Check
		send_welcome_email: DF.Check
		simultaneous_sessions: DF.Int
		social_logins: DF.Table[UserSocialLogin]
		thread_notify: DF.Check
		time_zone: DF.Autocomplete | None
		timeline: DF.Check
		university: DF.Literal["Abilene Christian University (TX)", "Abraham Baldwin Agricultural College (GA)", "Academy of Art University (CA)", "Acadia University (None)", "Adams State University (CO)", "Adelphi University (NY)", "Adrian College (MI)", "Adventist University of Health Sciences (FL)", "Agnes Scott College (GA)", "AIB College of Business (IA)", "Alabama Agricultural and Mechanical University (AL)", "Alabama State University (AL)", "Alaska Pacific University (AK)", "Albany College of Pharmacy and Health Sciences (NY)", "Albany State University (GA)", "Albertus Magnus College (CT)", "Albion College (MI)", "Albright College (PA)", "Alcorn State University (MS)", "Alderson Broaddus University (WV)", "Alfred University (NY)", "Alice Lloyd College (KY)", "Allegheny College (PA)", "Allen College (IA)", "Allen University (SC)", "Alliant International University (CA)", "Alma College (MI)", "Alvernia University (PA)", "Alverno College (WI)", "Amberton University (TX)", "American Academy of Art (IL)", "American Indian College of the Assemblies of God (AZ)", "American InterContinental University (IL)", "American International College (MA)", "American Jewish University (CA)", "American Public University System (WV)", "American University (DC)", "American University in Bulgaria (None)", "American University in Cairo (None)", "American University of Beirut (None)", "American University of Paris (None)", "American University of Puerto Rico (PR)", "Amherst College (MA)", "Amridge University (AL)", "Anderson University (IN)", "Anderson University (SC)", "Andrews University (MI)", "Angelo State University (TX)", "Anna Maria College (MA)", "Antioch University (OH)", "Appalachian Bible College (WV)", "Appalachian State University (NC)", "Aquinas College (MI)", "Aquinas College (TN)", "Arcadia University (PA)", "Argosy University (CA)", "Arizona Christian University (AZ)", "Arizona State University (AZ)", "Arizona State University--West (AZ)", "Arkansas Baptist College (AR)", "Arkansas State University (AR)", "Arkansas Tech University (AR)", "Armstrong Atlantic State University (GA)", "Art Academy of Cincinnati (OH)", "Art Center College of Design (CA)", "Art Institute of Atlanta (GA)", "Art Institute of Colorado (CO)", "Art Institute of Houston (TX)", "Art Institute of Pittsburgh (PA)", "Art Institute of Portland (OR)", "Art Institute of Seattle (WA)", "Asbury University (KY)", "Ashford University (IA)", "Ashland University (OH)", "Assumption College (MA)", "Athens State University (AL)", "Auburn University (AL)", "Auburn University--Montgomery (AL)", "Augsburg College (MN)", "Augustana College (IL)", "Augustana College (SD)", "Aurora University (IL)", "Austin College (TX)", "Austin Peay State University (TN)", "Ave Maria University (FL)", "Averett University (VA)", "Avila University (MO)", "Azusa Pacific University (CA)", "Babson College (MA)", "Bacone College (OK)", "Baker College of Flint (MI)", "Baker University (KS)", "Baldwin Wallace University (OH)", "Ball State University (IN)", "Baptist Bible College (MO)", "Baptist Bible College and Seminary (PA)", "Baptist College of Florida (FL)", "Baptist Memorial College of Health Sciences (TN)", "Baptist Missionary Association Theological Seminary (TX)", "Bard College (NY)", "Bard College at Simon's Rock (MA)", "Barnard College (NY)", "Barry University (FL)", "Barton College (NC)", "Bastyr University (WA)", "Bates College (ME)", "Bauder College (GA)", "Bay Path College (MA)", "Bay State College (MA)", "Bayamon Central University (PR)", "Baylor University (TX)", "Beacon College (FL)", "Becker College (MA)", "Belhaven University (MS)", "Bellarmine University (KY)", "Bellevue College (WA)", "Bellevue University (NE)", "Bellin College (WI)", "Belmont Abbey College (NC)", "Belmont University (TN)", "Beloit College (WI)", "Bemidji State University (MN)", "Benedict College (SC)", "Benedictine College (KS)", "Benedictine University (IL)", "Benjamin Franklin Institute of Technology (MA)", "Bennett College (NC)", "Bennington College (VT)", "Bentley University (MA)", "Berea College (KY)", "Berkeley College (NJ)", "Berkeley College (NY)", "Berklee College of Music (MA)", "Berry College (GA)", "Bethany College (KS)", "Bethany College (WV)", "Bethany Lutheran College (MN)", "Bethel College (IN)", "Bethel College (KS)", "Bethel University (TN)", "Bethel University (MN)", "Bethune-Cookman University (FL)", "BI Norwegian Business School (None)", "Binghamton University--SUNY (NY)", "Biola University (CA)", "Birmingham-Southern College (AL)", "Bismarck State College (ND)", "Black Hills State University (SD)", "Blackburn College (IL)", "Blessing-Rieman College of Nursing (IL)", "Bloomfield College (NJ)", "Bloomsburg University of Pennsylvania (PA)", "Blue Mountain College (MS)", "Bluefield College (VA)", "Bluefield State College (WV)", "Bluffton University (OH)", "Boise State University (ID)", "Boricua College (NY)", "Boston Architectural College (MA)", "Boston College (MA)", "Boston Conservatory (MA)", "Boston University (MA)", "Bowdoin College (ME)", "Bowie State University (MD)", "Bowling Green State University (OH)", "Bradley University (IL)", "Brandeis University (MA)", "Brandman University (CA)", "Brazosport College (TX)", "Brenau University (GA)", "Brescia University (KY)", "Brevard College (NC)", "Brewton-Parker College (GA)", "Briar Cliff University (IA)", "Briarcliffe College (NY)", "Bridgewater College (VA)", "Bridgewater State University (MA)", "Brigham Young University--Hawaii (HI)", "Brigham Young University--Idaho (ID)", "Brigham Young University--Provo (UT)", "Brock University (None)", "Brown University (RI)", "Bryan College (TN)", "Bryant University (RI)", "Bryn Athyn College of the New Church (PA)", "Bryn Mawr College (PA)", "Bucknell University (PA)", "Buena Vista University (IA)", "Burlington College (VT)", "Butler University (IN)", "Cabarrus College of Health Sciences (NC)", "Cabrini College (PA)", "Cairn University (PA)", "Caldwell College (NJ)", "California Baptist University (CA)", "California College of the Arts (CA)", "California Institute of Integral Studies (CA)", "California Institute of Technology (CA)", "California Institute of the Arts (CA)", "California Lutheran University (CA)", "California Maritime Academy (CA)", "California Polytechnic State University--San Luis Obispo (CA)", "California State Polytechnic University--Pomona (CA)", "California State University--Bakersfield (CA)", "California State University--Channel Islands (CA)", "California State University--Chico (CA)", "California State University--Dominguez Hills (CA)", "California State University--East Bay (CA)", "California State University--Fresno (CA)", "California State University--Fullerton (CA)", "California State University--Long Beach (CA)", "California State University--Los Angeles (CA)", "California State University--Monterey Bay (CA)", "California State University--Northridge (CA)", "California State University--Sacramento (CA)", "California State University--San Bernardino (CA)", "California State University--San Marcos (CA)", "California State University--Stanislaus (CA)", "California University of Pennsylvania (PA)", "Calumet College of St. Joseph (IN)", "Calvary Bible College and Theological Seminary (MO)", "Calvin College (MI)", "Cambridge College (MA)", "Cameron University (OK)", "Campbell University (NC)", "Campbellsville University (KY)", "Canisius College (NY)", "Capella University (MN)", "Capital University (OH)", "Capitol College (MD)", "Cardinal Stritch University (WI)", "Caribbean University (PR)", "Carleton College (MN)", "Carleton University (None)", "Carlos Albizu University (PR)", "Carlow University (PA)", "Carnegie Mellon University (PA)", "Carroll College (MT)", "Carroll University (WI)", "Carson-Newman University (TN)", "Carthage College (WI)", "Case Western Reserve University (OH)", "Castleton State College (VT)", "Catawba College (NC)", "Cazenovia College (NY)", "Cedar Crest College (PA)", "Cedarville University (OH)", "Centenary College (NJ)", "Centenary College of Louisiana (LA)", "Central Baptist College (AR)", "Central Bible College (MO)", "Central Christian College (KS)", "Central College (IA)", "Central Connecticut State University (CT)", "Central Methodist University (MO)", "Central Michigan University (MI)", "Central Penn College (PA)", "Central State University (OH)", "Central Washington University (WA)", "Centre College (KY)", "Chadron State College (NE)", "Chamberlain College of Nursing (IL)", "Chaminade University of Honolulu (HI)", "Champlain College (VT)", "Chancellor University (OH)", "Chapman University (CA)", "Charles R. Drew University of Medicine and Science (CA)", "Charleston Southern University (SC)", "Charter Oak State College (CT)", "Chatham University (PA)", "Chestnut Hill College (PA)", "Cheyney University of Pennsylvania (PA)", "Chicago State University (IL)", "Chipola College (FL)", "Chowan University (NC)", "Christendom College (VA)", "Christian Brothers University (TN)", "Christopher Newport University (VA)", "Cincinnati Christian University (OH)", "Cincinnati College of Mortuary Science (OH)", "City University of Seattle (WA)", "Claflin University (SC)", "Claremont McKenna College (CA)", "Clarion University of Pennsylvania (PA)", "Clark Atlanta University (GA)", "Clark University (MA)", "Clarke University (IA)", "Clarkson College (NE)", "Clarkson University (NY)", "Clayton State University (GA)", "Clear Creek Baptist Bible College (KY)", "Clearwater Christian College (FL)", "Cleary University (MI)", "Clemson University (SC)", "Cleveland Chiropractic College (MO)", "Cleveland Institute of Art (OH)", "Cleveland Institute of Music (OH)", "Cleveland State University (OH)", "Coastal Carolina University (SC)", "Coe College (IA)", "Cogswell Polytechnical College (CA)", "Coker College (SC)", "Colby College (ME)", "Colby-Sawyer College (NH)", "Colgate University (NY)", "College at Brockport--SUNY (NY)", "College for Creative Studies (MI)", "College of Charleston (SC)", "College of Idaho (ID)", "College of Mount St. Joseph (OH)", "College of Mount St. Vincent (NY)", "College of New Jersey (NJ)", "College of New Rochelle (NY)", "College of Our Lady of the Elms (MA)", "College of Saints John Fisher & Thomas More (TX)", "College of Southern Nevada (NV)", "College of St. Benedict (MN)", "College of St. Elizabeth (NJ)", "College of St. Joseph (VT)", "College of St. Mary (NE)", "College of St. Rose (NY)", "College of St. Scholastica (MN)", "College of the Atlantic (ME)", "College of the Holy Cross (MA)", "College of the Ozarks (MO)", "College of William and Mary (VA)", "College of Wooster (OH)", "Colorado Christian University (CO)", "Colorado College (CO)", "Colorado Mesa University (CO)", "Colorado School of Mines (CO)", "Colorado State University (CO)", "Colorado State University--Pueblo (CO)", "Colorado Technical University (CO)", "Columbia College (MO)", "Columbia College (SC)", "Columbia College Chicago (IL)", "Columbia College of Nursing (WI)", "Columbia International University (SC)", "Columbia University (NY)", "Columbus College of Art and Design (OH)", "Columbus State University (GA)", "Conception Seminary College (MO)", "Concord University (WV)", "Concordia College (AL)", "Concordia College (NY)", "Concordia College--Moorhead (MN)", "Concordia University (MI)", "Concordia University (NE)", "Concordia University (CA)", "Concordia University (OR)", "Concordia University (None)", "Concordia University Chicago (IL)", "Concordia University Texas (TX)", "Concordia University Wisconsin (WI)", "Concordia University--St. Paul (MN)", "Connecticut College (CT)", "Converse College (SC)", "Cooper Union (NY)", "Coppin State University (MD)", "Corban University (OR)", "Corcoran College of Art and Design (DC)", "Cornell College (IA)", "Cornell University (NY)", "Cornerstone University (MI)", "Cornish College of the Arts (WA)", "Covenant College (GA)", "Cox College (MO)", "Creighton University (NE)", "Criswell College (TX)", "Crown College (MN)", "Culinary Institute of America (NY)", "Culver-Stockton College (MO)", "Cumberland University (TN)", "CUNY--Baruch College (NY)", "CUNY--Brooklyn College (NY)", "CUNY--City College (NY)", "CUNY--College of Staten Island (NY)", "CUNY--Hunter College (NY)", "CUNY--John Jay College of Criminal Justice (NY)", "CUNY--Lehman College (NY)", "CUNY--Medgar Evers College (NY)", "CUNY--New York City College of Technology (NY)", "CUNY--Queens College (NY)", "CUNY--York College (NY)", "Curry College (MA)", "Curtis Institute of Music (PA)", "D'Youville College (NY)", "Daemen College (NY)", "Dakota State University (SD)", "Dakota Wesleyan University (SD)", "Dalhousie University (None)", "Dallas Baptist University (TX)", "Dallas Christian College (TX)", "Dalton State College (GA)", "Daniel Webster College (NH)", "Dartmouth College (NH)", "Davenport University (MI)", "Davidson College (NC)", "Davis and Elkins College (WV)", "Davis College (NY)", "Daytona State College (FL)", "Dean College (MA)", "Defiance College (OH)", "Delaware State University (DE)", "Delaware Valley College (PA)", "Delta State University (MS)", "Denison University (OH)", "DePaul University (IL)", "DePauw University (IN)", "DEREE--The American College of Greece (None)", "DeSales University (PA)", "DeVry University (IL)", "Dickinson College (PA)", "Dickinson State University (ND)", "Dillard University (LA)", "Divine Word College (IA)", "Dixie State College of Utah (UT)", "Doane College (NE)", "Dominican College (NY)", "Dominican University (IL)", "Dominican University of California (CA)", "Donnelly College (KS)", "Dordt College (IA)", "Dowling College (NY)", "Drake University (IA)", "Drew University (NJ)", "Drexel University (PA)", "Drury University (MO)", "Duke University (NC)", "Dunwoody College of Technology (MN)", "Duquesne University (PA)", "Earlham College (IN)", "East Carolina University (NC)", "East Central University (OK)", "East Stroudsburg University of Pennsylvania (PA)", "East Tennessee State University (TN)", "East Texas Baptist University (TX)", "East-West University (IL)", "Eastern Connecticut State University (CT)", "Eastern Illinois University (IL)", "Eastern Kentucky University (KY)", "Eastern Mennonite University (VA)", "Eastern Michigan University (MI)", "Eastern Nazarene College (MA)", "Eastern New Mexico University (NM)", "Eastern Oregon University (OR)", "Eastern University (PA)", "Eastern Washington University (WA)", "Eckerd College (FL)", "ECPI University (VA)", "Edgewood College (WI)", "Edinboro University of Pennsylvania (PA)", "Edison State College (FL)", "Edward Waters College (FL)", "Elizabeth City State University (NC)", "Elizabethtown College (PA)", "Elmhurst College (IL)", "Elmira College (NY)", "Elon University (NC)", "Embry-Riddle Aeronautical University (FL)", "Embry-Riddle Aeronautical University--Prescott (AZ)", "Emerson College (MA)", "Emmanuel College (GA)", "Emmanuel College (MA)", "Emmaus Bible College (IA)", "Emory and Henry College (VA)", "Emory University (GA)", "Emporia State University (KS)", "Endicott College (MA)", "Erskine College (SC)", "Escuela de Artes Plasticas de Puerto Rico (PR)", "Eureka College (IL)", "Evangel University (MO)", "Everest College--Phoenix (AZ)", "Everglades University (FL)", "Evergreen State College (WA)", "Excelsior College (NY)", "Fairfield University (CT)", "Fairleigh Dickinson University (NJ)", "Fairmont State University (WV)", "Faith Baptist Bible College and Theological Seminary (IA)", "Farmingdale State College--SUNY (NY)", "Fashion Institute of Technology (NY)", "Faulkner University (AL)", "Fayetteville State University (NC)", "Felician College (NJ)", "Ferris State University (MI)", "Ferrum College (VA)", "Finlandia University (MI)", "Fisher College (MA)", "Fisk University (TN)", "Fitchburg State University (MA)", "Five Towns College (NY)", "Flagler College (FL)", "Florida A&M University (FL)", "Florida Atlantic University (FL)", "Florida Christian College (FL)", "Florida College (FL)", "Florida Gulf Coast University (FL)", "Florida Institute of Technology (FL)", "Florida International University (FL)", "Florida Memorial University (FL)", "Florida Southern College (FL)", "Florida State College--Jacksonville (FL)", "Florida State University (FL)", "Fontbonne University (MO)", "Fordham University (NY)", "Fort Hays State University (KS)", "Fort Lewis College (CO)", "Fort Valley State University (GA)", "Framingham State University (MA)", "Francis Marion University (SC)", "Franciscan University of Steubenville (OH)", "Frank Lloyd Wright School of Architecture (AZ)", "Franklin and Marshall College (PA)", "Franklin College (IN)", "Franklin College Switzerland (None)", "Franklin Pierce University (NH)", "Franklin University (OH)", "Franklin W. Olin College of Engineering (MA)", "Freed-Hardeman University (TN)", "Fresno Pacific University (CA)", "Friends University (KS)", "Frostburg State University (MD)", "Furman University (SC)", "Gallaudet University (DC)", "Gannon University (PA)", "Gardner-Webb University (NC)", "Geneva College (PA)", "George Fox University (OR)", "George Mason University (VA)", "George Washington University (DC)", "Georgetown College (KY)", "Georgetown University (DC)", "Georgia College & State University (GA)", "Georgia Gwinnett College (GA)", "Georgia Institute of Technology (GA)", "Georgia Regents University (GA)", "Georgia Southern University (GA)", "Georgia Southwestern State University (GA)", "Georgia State University (GA)", "Georgian Court University (NJ)", "Gettysburg College (PA)", "Glenville State College (WV)", "God's Bible School and College (OH)", "Goddard College (VT)", "Golden Gate University (CA)", "Goldey-Beacom College (DE)", "Goldfarb School of Nursing at Barnes-Jewish College (MO)", "Gonzaga University (WA)", "Gordon College (MA)", "Gordon State College (GA)", "Goshen College (IN)", "Goucher College (MD)", "Governors State University (IL)", "Grace Bible College (MI)", "Grace College and Seminary (IN)", "Grace University (NE)", "Graceland University (IA)", "Grambling State University (LA)", "Grand Canyon University (AZ)", "Grand Valley State University (MI)", "Grand View University (IA)", "Granite State College (NH)", "Gratz College (PA)", "Great Basin College (NV)", "Great Lakes Christian College (MI)", "Green Mountain College (VT)", "Greensboro College (NC)", "Greenville College (IL)", "Grinnell College (IA)", "Grove City College (PA)", "Guilford College (NC)", "Gustavus Adolphus College (MN)", "Gwynedd-Mercy College (PA)", "Hamilton College (NY)", "Hamline University (MN)", "Hampden-Sydney College (VA)", "Hampshire College (MA)", "Hampton University (VA)", "Hannibal-LaGrange University (MO)", "Hanover College (IN)", "Hardin-Simmons University (TX)", "Harding University (AR)", "Harrington College of Design (IL)", "Harris-Stowe State University (MO)", "Harrisburg University of Science and Technology (PA)", "Hartwick College (NY)", "Harvard University (MA)", "Harvey Mudd College (CA)", "Haskell Indian Nations University (KS)", "Hastings College (NE)", "Haverford College (PA)", "Hawaii Pacific University (HI)", "Hebrew Theological College (IL)", "Heidelberg University (OH)", "Hellenic College (MA)", "Henderson State University (AR)", "Hendrix College (AR)", "Heritage University (WA)", "Herzing University (WI)", "High Point University (NC)", "Hilbert College (NY)", "Hillsdale College (MI)", "Hiram College (OH)", "Hobart and William Smith Colleges (NY)", "Hodges University (FL)", "Hofstra University (NY)", "Hollins University (VA)", "Holy Apostles College and Seminary (CT)", "Holy Cross College (IN)", "Holy Family University (PA)", "Holy Names University (CA)", "Hood College (MD)", "Hope College (MI)", "Hope International University (CA)", "Houghton College (NY)", "Houston Baptist University (TX)", "Howard Payne University (TX)", "Howard University (DC)", "Hult International Business School (None)", "Humboldt State University (CA)", "Humphreys College (CA)", "Huntingdon College (AL)", "Huntington University (IN)", "Husson University (ME)", "Huston-Tillotson University (TX)", "Idaho State University (ID)", "Illinois College (IL)", "Illinois Institute of Art at Chicago (IL)", "Illinois Institute of Technology (IL)", "Illinois State University (IL)", "Illinois Wesleyan University (IL)", "Immaculata University (PA)", "Indian River State College (FL)", "Indiana Institute of Technology (IN)", "Indiana State University (IN)", "Indiana University East (IN)", "Indiana University Northwest (IN)", "Indiana University of Pennsylvania (PA)", "Indiana University Southeast (IN)", "Indiana University--Bloomington (IN)", "Indiana University--Kokomo (IN)", "Indiana University--South Bend (IN)", "Indiana University-Purdue University--Fort Wayne (IN)", "Indiana University-Purdue University--Indianapolis (IN)", "Indiana Wesleyan University (IN)", "Institute of American Indian and Alaska Native Culture and Arts Development (NM)", "Inter American University of Puerto Rico--Aguadilla (PR)", "Inter American University of Puerto Rico--Arecibo (PR)", "Inter American University of Puerto Rico--Barranquitas (PR)", "Inter American University of Puerto Rico--Bayamon (PR)", "Inter American University of Puerto Rico--Fajardo (PR)", "Inter American University of Puerto Rico--Guayama (PR)", "Inter American University of Puerto Rico--Metropolitan Campus (PR)", "Inter American University of Puerto Rico--Ponce (PR)", "Inter American University of Puerto Rico--San German (PR)", "International College of the Cayman Islands (None)", "Iona College (NY)", "Iowa State University (IA)", "Iowa Wesleyan College (IA)", "Ithaca College (NY)", "Jackson State University (MS)", "Jacksonville State University (AL)", "Jacksonville University (FL)", "James Madison University (VA)", "Jarvis Christian College (TX)", "Jewish Theological Seminary of America (NY)", "John Brown University (AR)", "John Carroll University (OH)", "John F. Kennedy University (CA)", "Johns Hopkins University (MD)", "Johnson & Wales University (RI)", "Johnson C. Smith University (NC)", "Johnson State College (VT)", "Johnson University (TN)", "Jones International University (CO)", "Judson College (AL)", "Judson University (IL)", "Juilliard School (NY)", "Juniata College (PA)", "Kalamazoo College (MI)", "Kansas City Art Institute (MO)", "Kansas State University (KS)", "Kansas Wesleyan University (KS)", "Kaplan University (IA)", "Kean University (NJ)", "Keene State College (NH)", "Keiser University (FL)", "Kendall College (IL)", "Kennesaw State University (GA)", "Kent State University (OH)", "Kentucky Christian University (KY)", "Kentucky State University (KY)", "Kentucky Wesleyan College (KY)", "Kenyon College (OH)", "Kettering College (OH)", "Kettering University (MI)", "Keuka College (NY)", "Keystone College (PA)", "King University (TN)", "King's College (PA)", "King's College (NY)", "Knox College (IL)", "Kutztown University of Pennsylvania (PA)", "Kuyper College (MI)", "La Roche College (PA)", "La Salle University (PA)", "La Sierra University (CA)", "Lafayette College (PA)", "LaGrange College (GA)", "Laguna College of Art and Design (CA)", "Lake Erie College (OH)", "Lake Forest College (IL)", "Lake Superior State University (MI)", "Lakeland College (WI)", "Lakeview College of Nursing (IL)", "Lamar University (TX)", "Lancaster Bible College (PA)", "Lander University (SC)", "Lane College (TN)", "Langston University (OK)", "Lasell College (MA)", "Lawrence Technological University (MI)", "Lawrence University (WI)", "Le Moyne College (NY)", "Lebanon Valley College (PA)", "Lee University (TN)", "Lees-McRae College (NC)", "Lehigh University (PA)", "LeMoyne-Owen College (TN)", "Lenoir-Rhyne University (NC)", "Lesley University (MA)", "LeTourneau University (TX)", "Lewis & Clark College (OR)", "Lewis University (IL)", "Lewis-Clark State College (ID)", "Lexington College (IL)", "Liberty University (VA)", "Life Pacific College (CA)", "Life University (GA)", "LIM College (NY)", "Limestone College (SC)", "Lincoln Christian University (IL)", "Lincoln College (IL)", "Lincoln Memorial University (TN)", "Lincoln University (MO)", "Lincoln University (PA)", "Lindenwood University (MO)", "Lindsey Wilson College (KY)", "Linfield College (OR)", "Lipscomb University (TN)", "LIU Post (NY)", "Livingstone College (NC)", "Lock Haven University of Pennsylvania (PA)", "Loma Linda University (CA)", "Longwood University (VA)", "Loras College (IA)", "Louisiana College (LA)", "Louisiana State University Health Sciences Center (LA)", "Louisiana State University--Alexandria (LA)", "Louisiana State University--Baton Rouge (LA)", "Louisiana State University--Shreveport (LA)", "Louisiana Tech University (LA)", "Lourdes University (OH)", "Loyola Marymount University (CA)", "Loyola University Chicago (IL)", "Loyola University Maryland (MD)", "Loyola University New Orleans (LA)", "Lubbock Christian University (TX)", "Luther College (IA)", "Lycoming College (PA)", "Lyme Academy College of Fine Arts (CT)", "Lynchburg College (VA)", "Lyndon State College (VT)", "Lynn University (FL)", "Lyon College (AR)", "Macalester College (MN)", "MacMurray College (IL)", "Madonna University (MI)", "Maharishi University of Management (IA)", "Maine College of Art (ME)", "Maine Maritime Academy (ME)", "Malone University (OH)", "Manchester University (IN)", "Manhattan Christian College (KS)", "Manhattan College (NY)", "Manhattan School of Music (NY)", "Manhattanville College (NY)", "Mansfield University of Pennsylvania (PA)", "Maranatha Baptist Bible College (WI)", "Marian University (IN)", "Marian University (WI)", "Marietta College (OH)", "Marist College (NY)", "Marlboro College (VT)", "Marquette University (WI)", "Mars Hill University (NC)", "Marshall University (WV)", "Martin Luther College (MN)", "Martin Methodist College (TN)", "Martin University (IN)", "Mary Baldwin College (VA)", "Marygrove College (MI)", "Maryland Institute College of Art (MD)", "Marylhurst University (OR)", "Marymount Manhattan College (NY)", "Marymount University (VA)", "Maryville College (TN)", "Maryville University of St. Louis (MO)", "Marywood University (PA)", "Massachusetts College of Art and Design (MA)", "Massachusetts College of Liberal Arts (MA)", "Massachusetts College of Pharmacy and Health Sciences (MA)", "Massachusetts Institute of Technology (MA)", "Massachusetts Maritime Academy (MA)", "Master's College and Seminary (CA)", "Mayville State University (ND)", "McDaniel College (MD)", "McGill University (None)", "McKendree University (IL)", "McMurry University (TX)", "McNeese State University (LA)", "McPherson College (KS)", "Medaille College (NY)", "Medical University of South Carolina (SC)", "Memorial University of Newfoundland (None)", "Memphis College of Art (TN)", "Menlo College (CA)", "Mercer University (GA)", "Mercy College (NY)", "Mercy College of Health Sciences (IA)", "Mercy College of Ohio (OH)", "Mercyhurst University (PA)", "Meredith College (NC)", "Merrimack College (MA)", "Messiah College (PA)", "Methodist University (NC)", "Metropolitan College of New York (NY)", "Metropolitan State University (MN)", "Metropolitan State University of Denver (CO)", "Miami Dade College (FL)", "Miami International University of Art & Design (FL)", "Miami University--Oxford (OH)", "Michigan State University (MI)", "Michigan Technological University (MI)", "Mid-America Christian University (OK)", "Mid-Atlantic Christian University (NC)", "Mid-Continent University (KY)", "MidAmerica Nazarene University (KS)", "Middle Georgia State College (GA)", "Middle Tennessee State University (TN)", "Middlebury College (VT)", "Midland College (TX)", "Midland University (NE)", "Midstate College (IL)", "Midway College (KY)", "Midwestern State University (TX)", "Miles College (AL)", "Millersville University of Pennsylvania (PA)", "Milligan College (TN)", "Millikin University (IL)", "Mills College (CA)", "Millsaps College (MS)", "Milwaukee Institute of Art and Design (WI)", "Milwaukee School of Engineering (WI)", "Minneapolis College of Art and Design (MN)", "Minnesota State University--Mankato (MN)", "Minnesota State University--Moorhead (MN)", "Minot State University (ND)", "Misericordia University (PA)", "Mississippi College (MS)", "Mississippi State University (MS)", "Mississippi University for Women (MS)", "Mississippi Valley State University (MS)", "Missouri Baptist University (MO)", "Missouri Southern State University (MO)", "Missouri State University (MO)", "Missouri University of Science & Technology (MO)", "Missouri Valley College (MO)", "Missouri Western State University (MO)", "Mitchell College (CT)", "Molloy College (NY)", "Monmouth College (IL)", "Monmouth University (NJ)", "Monroe College (NY)", "Montana State University (MT)", "Montana State University--Billings (MT)", "Montana State University--Northern (MT)", "Montana Tech of the University of Montana (MT)", "Montclair State University (NJ)", "Monterrey Institute of Technology and Higher Education--Monterrey (None)", "Montreat College (NC)", "Montserrat College of Art (MA)", "Moody Bible Institute (IL)", "Moore College of Art & Design (PA)", "Moravian College (PA)", "Morehead State University (KY)", "Morehouse College (GA)", "Morgan State University (MD)", "Morningside College (IA)", "Morris College (SC)", "Morrisville State College (NY)", "Mount Aloysius College (PA)", "Mount Angel Seminary (OR)", "Mount Carmel College of Nursing (OH)", "Mount Holyoke College (MA)", "Mount Ida College (MA)", "Mount Marty College (SD)", "Mount Mary University (WI)", "Mount Mercy University (IA)", "Mount Olive College (NC)", "Mount St. Mary College (NY)", "Mount St. Mary's College (CA)", "Mount St. Mary's University (MD)", "Mount Vernon Nazarene University (OH)", "Mount Washington College (NH)", "Muhlenberg College (PA)", "Multnomah University (OR)", "Murray State University (KY)", "Muskingum University (OH)", "Naropa University (CO)", "National American University (SD)", "National Graduate School of Quality Management (MA)", "National Hispanic University (CA)", "National Labor College (MD)", "National University (CA)", "National-Louis University (IL)", "Nazarene Bible College (CO)", "Nazareth College (NY)", "Nebraska Methodist College (NE)", "Nebraska Wesleyan University (NE)", "Neumann University (PA)", "Nevada State College (NV)", "New College of Florida (FL)", "New England College (NH)", "New England Conservatory of Music (MA)", "New England Institute of Art (MA)", "New England Institute of Technology (RI)", "New Jersey City University (NJ)", "New Jersey Institute of Technology (NJ)", "New Mexico Highlands University (NM)", "New Mexico Institute of Mining and Technology (NM)", "New Mexico State University (NM)", "New Orleans Baptist Theological Seminary (LA)", "New School (NY)", "New York Institute of Technology (NY)", "New York University (NY)", "Newberry College (SC)", "Newbury College (MA)", "Newman University (KS)", "Niagara University (NY)", "Nicholls State University (LA)", "Nichols College (MA)", "Norfolk State University (VA)", "North Carolina A&T State University (NC)", "North Carolina Central University (NC)", "North Carolina State University--Raleigh (NC)", "North Carolina Wesleyan College (NC)", "North Central College (IL)", "North Central University (MN)", "North Dakota State University (ND)", "North Greenville University (SC)", "North Park University (IL)", "Northcentral University (AZ)", "Northeastern Illinois University (IL)", "Northeastern State University (OK)", "Northeastern University (MA)", "Northern Arizona University (AZ)", "Northern Illinois University (IL)", "Northern Kentucky University (KY)", "Northern Michigan University (MI)", "Northern New Mexico College (NM)", "Northern State University (SD)", "Northland College (WI)", "Northwest Christian University (OR)", "Northwest Florida State College (FL)", "Northwest Missouri State University (MO)", "Northwest Nazarene University (ID)", "Northwest University (WA)", "Northwestern College (IA)", "Northwestern Health Sciences University (MN)", "Northwestern Oklahoma State University (OK)", "Northwestern State University of Louisiana (LA)", "Northwestern University (IL)", "Northwood University (MI)", "Norwich University (VT)", "Notre Dame College of Ohio (OH)", "Notre Dame de Namur University (CA)", "Notre Dame of Maryland University (MD)", "Nova Scotia College of Art and Design (None)", "Nova Southeastern University (FL)", "Nyack College (NY)", "Oakland City University (IN)", "Oakland University (MI)", "Oakwood University (AL)", "Oberlin College (OH)", "Occidental College (CA)", "Oglala Lakota College (SD)", "Oglethorpe University (GA)", "Ohio Christian University (OH)", "Ohio Dominican University (OH)", "Ohio Northern University (OH)", "Ohio State University--Columbus (OH)", "Ohio University (OH)", "Ohio Valley University (WV)", "Ohio Wesleyan University (OH)", "Oklahoma Baptist University (OK)", "Oklahoma Christian University (OK)", "Oklahoma City University (OK)", "Oklahoma Panhandle State University (OK)", "Oklahoma State University (OK)", "Oklahoma State University Institute of Technology--Okmulgee (OK)", "Oklahoma State University--Oklahoma City (OK)", "Oklahoma Wesleyan University (OK)", "Old Dominion University (VA)", "Olivet College (MI)", "Olivet Nazarene University (IL)", "Olympic College (WA)", "Oral Roberts University (OK)", "Oregon College of Art and Craft (OR)", "Oregon Health and Science University (OR)", "Oregon Institute of Technology (OR)", "Oregon State University (OR)", "Otis College of Art and Design (CA)", "Ottawa University (KS)", "Otterbein University (OH)", "Ouachita Baptist University (AR)", "Our Lady of Holy Cross College (LA)", "Our Lady of the Lake College (LA)", "Our Lady of the Lake University (TX)", "Pace University (NY)", "Pacific Lutheran University (WA)", "Pacific Northwest College of Art (OR)", "Pacific Oaks College (CA)", "Pacific Union College (CA)", "Pacific University (OR)", "Paine College (GA)", "Palm Beach Atlantic University (FL)", "Palmer College of Chiropractic (IA)", "Park University (MO)", "Parker University (TX)", "Patten University (CA)", "Paul Smith's College (NY)", "Peirce College (PA)", "Peninsula College (WA)", "Pennsylvania College of Art and Design (PA)", "Pennsylvania College of Technology (PA)", "Pennsylvania State University--Erie, The Behrend College (PA)", "Pennsylvania State University--Harrisburg (PA)", "Pennsylvania State University--University Park (PA)", "Pepperdine University (CA)", "Peru State College (NE)", "Pfeiffer University (NC)", "Philadelphia University (PA)", "Philander Smith College (AR)", "Piedmont College (GA)", "Pine Manor College (MA)", "Pittsburg State University (KS)", "Pitzer College (CA)", "Plaza College (NY)", "Plymouth State University (NH)", "Point Loma Nazarene University (CA)", "Point Park University (PA)", "Point University (GA)", "Polytechnic Institute of New York University (NY)", "Pomona College (CA)", "Pontifical Catholic University of Puerto Rico (PR)", "Pontifical College Josephinum (OH)", "Portland State University (OR)", "Post University (CT)", "Potomac College (DC)", "Prairie View A&M University (TX)", "Pratt Institute (NY)", "Presbyterian College (SC)", "Prescott College (AZ)", "Presentation College (SD)", "Princeton University (NJ)", "Principia College (IL)", "Providence College (RI)", "Puerto Rico Conservatory of Music (PR)", "Purchase College--SUNY (NY)", "Purdue University--Calumet (IN)", "Purdue University--North Central (IN)", "Purdue University--West Lafayette (IN)", "Queens University of Charlotte (NC)", "Quincy University (IL)", "Quinnipiac University (CT)", "Radford University (VA)", "Ramapo College of New Jersey (NJ)", "Randolph College (VA)", "Randolph-Macon College (VA)", "Ranken Technical College (MO)", "Reed College (OR)", "Regent University (VA)", "Regent's American College London (None)", "Regis College (MA)", "Regis University (CO)", "Reinhardt University (GA)", "Rensselaer Polytechnic Institute (NY)", "Research College of Nursing (MO)", "Resurrection University (IL)", "Rhode Island College (RI)", "Rhode Island School of Design (RI)", "Rhodes College (TN)", "Rice University (TX)", "Richard Stockton College of New Jersey (NJ)", "Richmond--The American International University in London (None)", "Rider University (NJ)", "Ringling College of Art and Design (FL)", "Ripon College (WI)", "Rivier University (NH)", "Roanoke College (VA)", "Robert B. Miller College (MI)", "Robert Morris University (IL)", "Robert Morris University (PA)", "Roberts Wesleyan College (NY)", "Rochester College (MI)", "Rochester Institute of Technology (NY)", "Rockford University (IL)", "Rockhurst University (MO)", "Rocky Mountain College (MT)", "Rocky Mountain College of Art and Design (CO)", "Roger Williams University (RI)", "Rogers State University (OK)", "Rollins College (FL)", "Roosevelt University (IL)", "Rosalind Franklin University of Medicine and Science (IL)", "Rose-Hulman Institute of Technology (IN)", "Rosemont College (PA)", "Rowan University (NJ)", "Rush University (IL)", "Rust College (MS)", "Rutgers, the State University of New Jersey--Camden (NJ)", "Rutgers, the State University of New Jersey--New Brunswick (NJ)", "Rutgers, the State University of New Jersey--Newark (NJ)", "Ryerson University (None)", "Sacred Heart Major Seminary (MI)", "Sacred Heart University (CT)", "Saginaw Valley State University (MI)", "Salem College (NC)", "Salem International University (WV)", "Salem State University (MA)", "Salisbury University (MD)", "Salish Kootenai College (MT)", "Salve Regina University (RI)", "Sam Houston State University (TX)", "Samford University (AL)", "Samuel Merritt University (CA)", "San Diego Christian College (CA)", "San Diego State University (CA)", "San Francisco Art Institute (CA)", "San Francisco Conservatory of Music (CA)", "San Francisco State University (CA)", "San Jose State University (CA)", "Sanford College of Nursing (ND)", "Santa Clara University (CA)", "Santa Fe University of Art and Design (NM)", "Sarah Lawrence College (NY)", "Savannah College of Art and Design (GA)", "Savannah State University (GA)", "School of the Art Institute of Chicago (IL)", "School of Visual Arts (NY)", "Schreiner University (TX)", "Scripps College (CA)", "Seattle Pacific University (WA)", "Seattle University (WA)", "Seton Hall University (NJ)", "Seton Hill University (PA)", "Sewanee--University of the South (TN)", "Shaw University (NC)", "Shawnee State University (OH)", "Shenandoah University (VA)", "Shepherd University (WV)", "Shimer College (IL)", "Shippensburg University of Pennsylvania (PA)", "Shorter University (GA)", "Siena College (NY)", "Siena Heights University (MI)", "Sierra Nevada College (NV)", "Silver Lake College (WI)", "Simmons College (MA)", "Simon Fraser University (None)", "Simpson College (IA)", "Simpson University (CA)", "Sinte Gleska University (SD)", "Sitting Bull College (ND)", "Skidmore College (NY)", "Slippery Rock University of Pennsylvania (PA)", "Smith College (MA)", "Sojourner-Douglass College (MD)", "Soka University of America (CA)", "Sonoma State University (CA)", "South Carolina State University (SC)", "South College (TN)", "South Dakota School of Mines and Technology (SD)", "South Dakota State University (SD)", "South Seattle Community College (WA)", "South Texas College (TX)", "South University (GA)", "Southeast Missouri State University (MO)", "Southeastern Louisiana University (LA)", "Southeastern Oklahoma State University (OK)", "Southeastern University (FL)", "Southern Adventist University (TN)", "Southern Arkansas University (AR)", "Southern Baptist Theological Seminary (KY)", "Southern California Institute of Architecture (CA)", "Southern Connecticut State University (CT)", "Southern Illinois University--Carbondale (IL)", "Southern Illinois University--Edwardsville (IL)", "Southern Methodist University (TX)", "Southern Nazarene University (OK)", "Southern New Hampshire University (NH)", "Southern Oregon University (OR)", "Southern Polytechnic State University (GA)", "Southern University and A&M College (LA)", "Southern University--New Orleans (LA)", "Southern Utah University (UT)", "Southern Vermont College (VT)", "Southern Wesleyan University (SC)", "Southwest Baptist University (MO)", "Southwest Minnesota State University (MN)", "Southwest University of Visual Arts (AZ)", "Southwestern Adventist University (TX)", "Southwestern Assemblies of God University (TX)", "Southwestern Christian College (TX)", "Southwestern Christian University (OK)", "Southwestern College (KS)", "Southwestern Oklahoma State University (OK)", "Southwestern University (TX)", "Spalding University (KY)", "Spelman College (GA)", "Spring Arbor University (MI)", "Spring Hill College (AL)", "Springfield College (MA)", "St. Ambrose University (IA)", "St. Anselm College (NH)", "St. Anthony College of Nursing (IL)", "St. Augustine College (IL)", "St. Augustine's University (NC)", "St. Bonaventure University (NY)", "St. Catharine College (KY)", "St. Catherine University (MN)", "St. Charles Borromeo Seminary (PA)", "St. Cloud State University (MN)", "St. Edward's University (TX)", "St. Francis College (NY)", "St. Francis Medical Center College of Nursing (IL)", "St. Francis University (PA)", "St. Gregory's University (OK)", "St. John Fisher College (NY)", "St. John Vianney College Seminary (FL)", "St. John's College (MD)", "St. John's College (NM)", "St. John's College (IL)", "St. John's University (MN)", "St. John's University (NY)", "St. Joseph Seminary College (LA)", "St. Joseph's College (IN)", "St. Joseph's College (ME)", "St. Joseph's College New York (NY)", "St. Joseph's University (PA)", "St. Lawrence University (NY)", "St. Leo University (FL)", "St. Louis College of Pharmacy (MO)", "St. Louis University (MO)", "St. Luke's College of Health Sciences (MO)", "St. Martin's University (WA)", "St. Mary's College (IN)", "St. Mary's College of California (CA)", "St. Mary's College of Maryland (MD)", "St. Mary's Seminary and University (MD)", "St. Mary's University of Minnesota (MN)", "St. Mary's University of San Antonio (TX)", "St. Mary-of-the-Woods College (IN)", "St. Michael's College (VT)", "St. Norbert College (WI)", "St. Olaf College (MN)", "St. Paul's College (VA)", "St. Peter's University (NJ)", "St. Petersburg College (FL)", "St. Thomas Aquinas College (NY)", "St. Thomas University (FL)", "St. Vincent College (PA)", "St. Xavier University (IL)", "Stanford University (CA)", "Stephen F. Austin State University (TX)", "Stephens College (MO)", "Sterling College (KS)", "Sterling College (VT)", "Stetson University (FL)", "Stevens Institute of Technology (NJ)", "Stevenson University (MD)", "Stillman College (AL)", "Stonehill College (MA)", "Stony Brook University--SUNY (NY)", "Strayer University (DC)", "Suffolk University (MA)", "Sul Ross State University (TX)", "Sullivan University (KY)", "SUNY Buffalo State (NY)", "SUNY College of Agriculture and Technology--Cobleskill (NY)", "SUNY College of Environmental Science and Forestry (NY)", "SUNY College of Technology--Alfred (NY)", "SUNY College of Technology--Canton (NY)", "SUNY College of Technology--Delhi (NY)", "SUNY College--Cortland (NY)", "SUNY College--Old Westbury (NY)", "SUNY College--Oneonta (NY)", "SUNY College--Potsdam (NY)", "SUNY Downstate Medical Center (NY)", "SUNY Empire State College (NY)", "SUNY Institute of Technology--Utica/Rome (NY)", "SUNY Maritime College (NY)", "SUNY Upstate Medical University (NY)", "SUNY--Fredonia (NY)", "SUNY--Geneseo (NY)", "SUNY--New Paltz (NY)", "SUNY--Oswego (NY)", "SUNY--Plattsburgh (NY)", "Susquehanna University (PA)", "Swarthmore College (PA)", "Sweet Briar College (VA)", "Syracuse University (NY)", "Tabor College (KS)", "Talladega College (AL)", "Tarleton State University (TX)", "Taylor University (IN)", "Temple University (PA)", "Tennessee State University (TN)", "Tennessee Technological University (TN)", "Tennessee Wesleyan College (TN)", "Texas A&M International University (TX)", "Texas A&M University--College Station (TX)", "Texas A&M University--Commerce (TX)", "Texas A&M University--Corpus Christi (TX)", "Texas A&M University--Galveston (TX)", "Texas A&M University--Kingsville (TX)", "Texas A&M University--Texarkana (TX)", "Texas Christian University (TX)", "Texas College (TX)", "Texas Lutheran University (TX)", "Texas Southern University (TX)", "Texas State University (TX)", "Texas Tech University (TX)", "Texas Tech University Health Sciences Center (TX)", "Texas Wesleyan University (TX)", "Texas Woman's University (TX)", "The Catholic University of America (DC)", "The Citadel (SC)", "The Sage Colleges (NY)", "Thiel College (PA)", "Thomas Aquinas College (CA)", "Thomas College (ME)", "Thomas Edison State College (NJ)", "Thomas Jefferson University (PA)", "Thomas More College (KY)", "Thomas More College of Liberal Arts (NH)", "Thomas University (GA)", "Tiffin University (OH)", "Tilburg University (None)", "Toccoa Falls College (GA)", "Tougaloo College (MS)", "Touro College (NY)", "Towson University (MD)", "Transylvania University (KY)", "Trent University (None)", "Trevecca Nazarene University (TN)", "Trident University International (CA)", "Trine University (IN)", "Trinity Christian College (IL)", "Trinity College (CT)", "Trinity College of Nursing & Health Sciences (IL)", "Trinity International University (IL)", "Trinity Lutheran College (WA)", "Trinity University (DC)", "Trinity University (TX)", "Trinity Western University (None)", "Troy University (AL)", "Truett McConnell College (GA)", "Truman State University (MO)", "Tufts University (MA)", "Tulane University (LA)", "Tusculum College (TN)", "Tuskegee University (AL)", "Union College (KY)", "Union College (NE)", "Union College (NY)", "Union Institute and University (OH)", "Union University (TN)", "United States Air Force Academy (CO)", "United States Coast Guard Academy (CT)", "United States International University--Kenya (None)", "United States Merchant Marine Academy (NY)", "United States Military Academy (NY)", "United States Naval Academy (MD)", "United States Sports Academy (AL)", "Unity College (ME)", "Universidad Adventista de las Antillas (PR)", "Universidad del Este (PR)", "Universidad del Turabo (PR)", "Universidad Metropolitana (PR)", "Universidad Politecnica De Puerto Rico (PR)", "University at Albany--SUNY (NY)", "University at Buffalo--SUNY (NY)", "University of Advancing Technology (AZ)", "University of Akron (OH)", "University of Alabama (AL)", "University of Alabama--Birmingham (AL)", "University of Alabama--Huntsville (AL)", "University of Alaska--Anchorage (AK)", "University of Alaska--Fairbanks (AK)", "University of Alaska--Southeast (AK)", "University of Alberta (None)", "University of Arizona (AZ)", "University of Arkansas (AR)", "University of Arkansas for Medical Sciences (AR)", "University of Arkansas--Fort Smith (AR)", "University of Arkansas--Little Rock (AR)", "University of Arkansas--Monticello (AR)", "University of Arkansas--Pine Bluff (AR)", "University of Baltimore (MD)", "University of Bridgeport (CT)", "University of British Columbia (None)", "University of Calgary (None)", "University of California--Berkeley (CA)", "University of California--Davis (CA)", "University of California--Irvine (CA)", "University of California--Los Angeles (CA)", "University of California--Riverside (CA)", "University of California--San Diego (CA)", "University of California--Santa Barbara (CA)", "University of California--Santa Cruz (CA)", "University of Central Arkansas (AR)", "University of Central Florida (FL)", "University of Central Missouri (MO)", "University of Central Oklahoma (OK)", "University of Charleston (WV)", "University of Chicago (IL)", "University of Cincinnati (OH)", "University of Cincinnati--UC Blue Ash College (OH)", "University of Colorado--Boulder (CO)", "University of Colorado--Colorado Springs (CO)", "University of Colorado--Denver (CO)", "University of Connecticut (CT)", "University of Dallas (TX)", "University of Dayton (OH)", "University of Delaware (DE)", "University of Denver (CO)", "University of Detroit Mercy (MI)", "University of Dubuque (IA)", "University of Evansville (IN)", "University of Findlay (OH)", "University of Florida (FL)", "University of Georgia (GA)", "University of Great Falls (MT)", "University of Guam (GU)", "University of Guelph (None)", "University of Hartford (CT)", "University of Hawaii--Hilo (HI)", "University of Hawaii--Manoa (HI)", "University of Hawaii--Maui College (HI)", "University of Hawaii--West Oahu (HI)", "University of Houston (TX)", "University of Houston--Clear Lake (TX)", "University of Houston--Downtown (TX)", "University of Houston--Victoria (TX)", "University of Idaho (ID)", "University of Illinois--Chicago (IL)", "University of Illinois--Springfield (IL)", "University of Illinois--Urbana-Champaign (IL)", "University of Indianapolis (IN)", "University of Iowa (IA)", "University of Jamestown (ND)", "University of Kansas (KS)", "University of Kentucky (KY)", "University of La Verne (CA)", "University of Louisiana--Lafayette (LA)", "University of Louisiana--Monroe (LA)", "University of Louisville (KY)", "University of Maine (ME)", "University of Maine--Augusta (ME)", "University of Maine--Farmington (ME)", "University of Maine--Fort Kent (ME)", "University of Maine--Machias (ME)", "University of Maine--Presque Isle (ME)", "University of Mary (ND)", "University of Mary Hardin-Baylor (TX)", "University of Mary Washington (VA)", "University of Maryland--Baltimore (MD)", "University of Maryland--Baltimore County (MD)", "University of Maryland--College Park (MD)", "University of Maryland--Eastern Shore (MD)", "University of Maryland--University College (MD)", "University of Massachusetts--Amherst (MA)", "University of Massachusetts--Boston (MA)", "University of Massachusetts--Dartmouth (MA)", "University of Massachusetts--Lowell (MA)", "University of Medicine and Dentistry of New Jersey (NJ)", "University of Memphis (TN)", "University of Miami (FL)", "University of Michigan--Ann Arbor (MI)", "University of Michigan--Dearborn (MI)", "University of Michigan--Flint (MI)", "University of Minnesota--Crookston (MN)", "University of Minnesota--Duluth (MN)", "University of Minnesota--Morris (MN)", "University of Minnesota--Twin Cities (MN)", "University of Mississippi (MS)", "University of Mississippi Medical Center (MS)", "University of Missouri (MO)", "University of Missouri--Kansas City (MO)", "University of Missouri--St. Louis (MO)", "University of Mobile (AL)", "University of Montana (MT)", "University of Montana--Western (MT)", "University of Montevallo (AL)", "University of Mount Union (OH)", "University of Nebraska Medical Center (NE)", "University of Nebraska--Kearney (NE)", "University of Nebraska--Lincoln (NE)", "University of Nebraska--Omaha (NE)", "University of Nevada--Las Vegas (NV)", "University of Nevada--Reno (NV)", "University of New Brunswick (None)", "University of New England (ME)", "University of New Hampshire (NH)", "University of New Haven (CT)", "University of New Mexico (NM)", "University of New Orleans (LA)", "University of North Alabama (AL)", "University of North Carolina School of the Arts (NC)", "University of North Carolina--Asheville (NC)", "University of North Carolina--Chapel Hill (NC)", "University of North Carolina--Charlotte (NC)", "University of North Carolina--Greensboro (NC)", "University of North Carolina--Pembroke (NC)", "University of North Carolina--Wilmington (NC)", "University of North Dakota (ND)", "University of North Florida (FL)", "University of North Georgia (GA)", "University of North Texas (TX)", "University of Northern Colorado (CO)", "University of Northern Iowa (IA)", "University of Northwestern Ohio (OH)", "University of Northwestern--St. Paul (MN)", "University of Notre Dame (IN)", "University of Oklahoma (OK)", "University of Oregon (OR)", "University of Ottawa (None)", "University of Pennsylvania (PA)", "University of Phoenix (AZ)", "University of Pikeville (KY)", "University of Pittsburgh (PA)", "University of Portland (OR)", "University of Prince Edward Island (None)", "University of Puerto Rico--Aguadilla (PR)", "University of Puerto Rico--Arecibo (PR)", "University of Puerto Rico--Bayamon (PR)", "University of Puerto Rico--Cayey (PR)", "University of Puerto Rico--Humacao (PR)", "University of Puerto Rico--Mayaguez (PR)", "University of Puerto Rico--Medical Sciences Campus (PR)", "University of Puerto Rico--Ponce (PR)", "University of Puerto Rico--Rio Piedras (PR)", "University of Puget Sound (WA)", "University of Redlands (CA)", "University of Regina (None)", "University of Rhode Island (RI)", "University of Richmond (VA)", "University of Rio Grande (OH)", "University of Rochester (NY)", "University of San Diego (CA)", "University of San Francisco (CA)", "University of Saskatchewan (None)", "University of Science and Arts of Oklahoma (OK)", "University of Scranton (PA)", "University of Sioux Falls (SD)", "University of South Alabama (AL)", "University of South Carolina (SC)", "University of South Carolina--Aiken (SC)", "University of South Carolina--Beaufort (SC)", "University of South Carolina--Upstate (SC)", "University of South Dakota (SD)", "University of South Florida (FL)", "University of South Florida--St. Petersburg (FL)", "University of Southern California (CA)", "University of Southern Indiana (IN)", "University of Southern Maine (ME)", "University of Southern Mississippi (MS)", "University of St. Francis (IL)", "University of St. Francis (IN)", "University of St. Joseph (CT)", "University of St. Mary (KS)", "University of St. Thomas (MN)", "University of St. Thomas (TX)", "University of Tampa (FL)", "University of Tennessee (TN)", "University of Tennessee--Chattanooga (TN)", "University of Tennessee--Martin (TN)", "University of Texas Health Science Center--Houston (TX)", "University of Texas Health Science Center--San Antonio (TX)", "University of Texas Medical Branch--Galveston (TX)", "University of Texas of the Permian Basin (TX)", "University of Texas--Arlington (TX)", "University of Texas--Austin (TX)", "University of Texas--Brownsville (TX)", "University of Texas--Dallas (TX)", "University of Texas--El Paso (TX)", "University of Texas--Pan American (TX)", "University of Texas--San Antonio (TX)", "University of Texas--Tyler (TX)", "University of the Arts (PA)", "University of the Cumberlands (KY)", "University of the District of Columbia (DC)", "University of the Incarnate Word (TX)", "University of the Ozarks (AR)", "University of the Pacific (CA)", "University of the Sacred Heart (PR)", "University of the Sciences (PA)", "University of the Southwest (NM)", "University of the Virgin Islands (VI)", "University of the West (CA)", "University of Toledo (OH)", "University of Toronto (None)", "University of Tulsa (OK)", "University of Utah (UT)", "University of Vermont (VT)", "University of Victoria (None)", "University of Virginia (VA)", "University of Virginia--Wise (VA)", "University of Washington (WA)", "University of Waterloo (None)", "University of West Alabama (AL)", "University of West Florida (FL)", "University of West Georgia (GA)", "University of Windsor (None)", "University of Winnipeg (None)", "University of Wisconsin--Eau Claire (WI)", "University of Wisconsin--Green Bay (WI)", "University of Wisconsin--La Crosse (WI)", "University of Wisconsin--Madison (WI)", "University of Wisconsin--Milwaukee (WI)", "University of Wisconsin--Oshkosh (WI)", "University of Wisconsin--Parkside (WI)", "University of Wisconsin--Platteville (WI)", "University of Wisconsin--River Falls (WI)", "University of Wisconsin--Stevens Point (WI)", "University of Wisconsin--Stout (WI)", "University of Wisconsin--Superior (WI)", "University of Wisconsin--Whitewater (WI)", "University of Wyoming (WY)", "Upper Iowa University (IA)", "Urbana University (OH)", "Ursinus College (PA)", "Ursuline College (OH)", "Utah State University (UT)", "Utah Valley University (UT)", "Utica College (NY)", "Valdosta State University (GA)", "Valley City State University (ND)", "Valley Forge Christian College (PA)", "Valparaiso University (IN)", "Vanderbilt University (TN)", "VanderCook College of Music (IL)", "Vanguard University of Southern California (CA)", "Vassar College (NY)", "Vaughn College of Aeronautics and Technology (NY)", "Vermont Technical College (VT)", "Victory University (TN)", "Villanova University (PA)", "Vincennes University (IN)", "Virginia Commonwealth University (VA)", "Virginia Intermont College (VA)", "Virginia Military Institute (VA)", "Virginia State University (VA)", "Virginia Tech (VA)", "Virginia Union University (VA)", "Virginia Wesleyan College (VA)", "Viterbo University (WI)", "Voorhees College (SC)", "Wabash College (IN)", "Wagner College (NY)", "Wake Forest University (NC)", "Walden University (MN)", "Waldorf College (IA)", "Walla Walla University (WA)", "Walsh College of Accountancy and Business Administration (MI)", "Walsh University (OH)", "Warner Pacific College (OR)", "Warner University (FL)", "Warren Wilson College (NC)", "Wartburg College (IA)", "Washburn University (KS)", "Washington Adventist University (MD)", "Washington and Jefferson College (PA)", "Washington and Lee University (VA)", "Washington College (MD)", "Washington State University (WA)", "Washington University in St. Louis (MO)", "Watkins College of Art, Design & Film (TN)", "Wayland Baptist University (TX)", "Wayne State College (NE)", "Wayne State University (MI)", "Waynesburg University (PA)", "Webb Institute (NY)", "Webber International University (FL)", "Weber State University (UT)", "Webster University (MO)", "Welch College (TN)", "Wellesley College (MA)", "Wells College (NY)", "Wentworth Institute of Technology (MA)", "Wesley College (DE)", "Wesleyan College (GA)", "Wesleyan University (CT)", "West Chester University of Pennsylvania (PA)", "West Liberty University (WV)", "West Texas A&M University (TX)", "West Virginia State University (WV)", "West Virginia University (WV)", "West Virginia University Institute of Technology (WV)", "West Virginia University--Parkersburg (WV)", "West Virginia Wesleyan College (WV)", "Western Carolina University (NC)", "Western Connecticut State University (CT)", "Western Governors University (UT)", "Western Illinois University (IL)", "Western International University (AZ)", "Western Kentucky University (KY)", "Western Michigan University (MI)", "Western Nevada College (NV)", "Western New England University (MA)", "Western New Mexico University (NM)", "Western Oregon University (OR)", "Western State Colorado University (CO)", "Western University (None)", "Western Washington University (WA)", "Westfield State University (MA)", "Westminster College (MO)", "Westminster College (PA)", "Westminster College (UT)", "Westmont College (CA)", "Wheaton College (IL)", "Wheaton College (MA)", "Wheeling Jesuit University (WV)", "Wheelock College (MA)", "Whitman College (WA)", "Whittier College (CA)", "Whitworth University (WA)", "Wichita State University (KS)", "Widener University (PA)", "Wilberforce University (OH)", "Wiley College (TX)", "Wilkes University (PA)", "Willamette University (OR)", "William Carey University (MS)", "William Jessup University (CA)", "William Jewell College (MO)", "William Paterson University of New Jersey (NJ)", "William Peace University (NC)", "William Penn University (IA)", "William Woods University (MO)", "Williams Baptist College (AR)", "Williams College (MA)", "Wilmington College (OH)", "Wilmington University (DE)", "Wilson College (PA)", "Wingate University (NC)", "Winona State University (MN)", "Winston-Salem State University (NC)", "Winthrop University (SC)", "Wisconsin Lutheran College (WI)", "Wittenberg University (OH)", "Wofford College (SC)", "Woodbury University (CA)", "Worcester Polytechnic Institute (MA)", "Worcester State University (MA)", "Wright State University (OH)", "Xavier University (OH)", "Xavier University of Louisiana (LA)", "Yale University (CT)", "Yeshiva University (NY)", "York College (NE)", "York College of Pennsylvania (PA)", "York University (None)", "Youngstown State University (OH)", "None"]
		unsubscribed: DF.Check
		user_emails: DF.Table[UserEmail]
		user_image: DF.AttachImage | None
		user_type: DF.Link | None
		user_website: DF.Data | None
		username: DF.Data | None
		view_switcher: DF.Check
	# end: auto-generated types

	__new_password = None

	def __setup__(self):
		# because it is handled separately
		self.flags.ignore_save_passwords = ["new_password"]

	def autoname(self):
		"""set name as Email Address"""
		if self.get("is_admin") or self.get("is_guest"):
			self.name = self.first_name
		else:
			self.email = self.email.strip().lower()
			self.name = self.email

	def onload(self):
		from frappe.utils.modules import get_modules_from_all_apps

		self.set_onload("all_modules", sorted(m.get("module_name") for m in get_modules_from_all_apps()))

	def before_insert(self):
		self.flags.in_insert = True
		throttle_user_creation()

	def after_insert(self):
		create_notification_settings(self.name)
		frappe.cache.delete_key("users_for_mentions")
		frappe.cache.delete_key("enabled_users")

	def validate(self):
		# clear new password
		self.__new_password = self.new_password
		self.new_password = ""

		if not frappe.flags.in_test:
			self.password_strength_test()

		if self.name not in STANDARD_USERS:
			self.email = self.name
			self.validate_email_type(self.name)

		self.move_role_profile_name_to_role_profiles()
		self.populate_role_profile_roles()
		self.check_roles_added()
		self.set_system_user()
		self.set_full_name()
		self.check_enable_disable()
		self.ensure_unique_roles()
		self.ensure_unique_role_profiles()
		self.remove_all_roles_for_guest()
		self.validate_username()
		self.remove_disabled_roles()
		self.validate_user_email_inbox()
		if self.user_emails:
			ask_pass_update()
		self.validate_allowed_modules()
		self.validate_user_image()
		self.set_time_zone()

		if self.language == "Loading...":
			self.language = None

		if (self.name not in ["Administrator", "Guest"]) and (not self.get_social_login_userid("frappe")):
			self.set_social_login_userid("frappe", frappe.generate_hash(length=39))

	def disable_email_fields_if_user_disabled(self):
		if not self.enabled:
			self.thread_notify = 0
			self.send_me_a_copy = 0
			self.allowed_in_mentions = 0

	@frappe.whitelist()
	def populate_role_profile_roles(self):
		if not self.role_profiles:
			return

		if self.name in STANDARD_USERS:
			self.role_profiles = []
			return

		new_roles = set()
		for role_profile in self.role_profiles:
			role_profile = frappe.get_cached_doc("Role Profile", role_profile.role_profile)
			new_roles.update(role.role for role in role_profile.roles)

		# Remove invalid roles and add new ones
		self.roles = [r for r in self.roles if r.role in new_roles]
		self.append_roles(*new_roles)

	from frappe.deprecation_dumpster import validate_roles

	def move_role_profile_name_to_role_profiles(self):
		"""This handles old role_profile_name field if programatically set.

		This behaviour will be remoed in future versions."""
		if not self.role_profile_name:
			return

		current_role_profiles = [r.role_profile for r in self.role_profiles]
		if self.role_profile_name in current_role_profiles:
			self.role_profile_name = None
			return

		from frappe.deprecation_dumpster import deprecation_warning

		deprecation_warning(
			"unknown",
			"v16",
			"The field `role_profile_name` is deprecated and will be removed in v16, use `role_profiles` child table instead.",
		)
		self.append("role_profiles", {"role_profile": self.role_profile_name})
		self.role_profile_name = None

	def validate_allowed_modules(self):
		if self.module_profile:
			module_profile = frappe.get_doc("Module Profile", self.module_profile)
			self.set("block_modules", [])
			for d in module_profile.get("block_modules"):
				self.append("block_modules", {"module": d.module})

	def validate_user_image(self):
		if self.user_image and len(self.user_image) > 2000:
			frappe.throw(_("Not a valid User Image."))

	def on_update(self):
		# clear new password
		self.share_with_self()
		clear_notifications(user=self.name)
		frappe.clear_cache(user=self.name)
		now = frappe.flags.in_test or frappe.flags.in_install
		self.send_password_notification(self.__new_password)
		frappe.enqueue(
			"frappe.core.doctype.user.user.create_contact",
			user=self,
			ignore_mandatory=True,
			now=now,
			enqueue_after_commit=True,
		)

		if self.name not in STANDARD_USERS and not self.user_image:
			frappe.enqueue(
				"frappe.core.doctype.user.user.update_gravatar",
				name=self.name,
				now=now,
				enqueue_after_commit=True,
			)

		# Set user selected timezone
		if self.time_zone:
			frappe.defaults.set_default("time_zone", self.time_zone, self.name)

		if self.has_value_changed("language"):
			locale_keys = ("date_format", "time_format", "number_format", "first_day_of_the_week")
			if self.language:
				language = frappe.get_doc("Language", self.language)
				for key in locale_keys:
					value = language.get(key)
					if value:
						frappe.defaults.set_default(key, value, self.name)
			else:
				for key in locale_keys:
					frappe.defaults.clear_default(key, parent=self.name)

		if self.has_value_changed("enabled"):
			frappe.cache.delete_key("users_for_mentions")
			frappe.cache.delete_key("enabled_users")
		elif self.has_value_changed("allow_in_mentions") or self.has_value_changed("user_type"):
			frappe.cache.delete_key("users_for_mentions")

	def has_website_permission(self, ptype, user, verbose=False):
		"""Return True if current user is the session user."""
		return self.name == frappe.session.user

	def set_full_name(self):
		self.full_name = " ".join(filter(None, [self.first_name, self.last_name]))

	def check_enable_disable(self):
		# do not allow disabling administrator/guest
		if not cint(self.enabled) and self.name in STANDARD_USERS:
			frappe.throw(_("User {0} cannot be disabled").format(self.name))

		# clear sessions if disabled
		if not cint(self.enabled) and getattr(frappe.local, "login_manager", None):
			frappe.local.login_manager.logout(user=self.name)

		# toggle notifications based on the user's status
		toggle_notifications(self.name, enable=cint(self.enabled), ignore_permissions=True)
		self.disable_email_fields_if_user_disabled()

	def email_new_password(self, new_password=None):
		if new_password and not self.flags.in_insert:
			_update_password(user=self.name, pwd=new_password, logout_all_sessions=self.logout_all_sessions)

	def set_system_user(self):
		"""For the standard users like admin and guest, the user type is fixed."""
		user_type_mapper = {"Administrator": "System User", "Guest": "Website User"}

		if self.user_type and not frappe.get_cached_value("User Type", self.user_type, "is_standard"):
			if user_type_mapper.get(self.name):
				self.user_type = user_type_mapper.get(self.name)
			else:
				self.set_roles_and_modules_based_on_user_type()
		else:
			"""Set as System User if any of the given roles has desk_access"""
			self.user_type = "System User" if self.has_desk_access() else "Website User"

	def set_roles_and_modules_based_on_user_type(self):
		user_type_doc = frappe.get_cached_doc("User Type", self.user_type)
		if user_type_doc.role:
			self.roles = []

			# Check whether User has linked with the 'Apply User Permission On' doctype or not
			if user_linked_with_permission_on_doctype(user_type_doc, self.name):
				self.append("roles", {"role": user_type_doc.role})

				frappe.msgprint(
					_("Role has been set as per the user type {0}").format(self.user_type), alert=True
				)

		user_type_doc.update_modules_in_user(self)

	def has_desk_access(self):
		"""Return true if any of the set roles has desk access"""
		if not self.roles:
			return False

		role_table = DocType("Role")
		return frappe.db.count(
			role_table,
			((role_table.desk_access == 1) & (role_table.name.isin([d.role for d in self.roles]))),
		)

	def share_with_self(self):
		if self.name in STANDARD_USERS:
			return

		frappe.share.add_docshare(
			self.doctype, self.name, self.name, write=1, share=1, flags={"ignore_share_permission": True}
		)

	def validate_share(self, docshare):
		pass
		# if docshare.user == self.name:
		# 	if self.user_type=="System User":
		# 		if docshare.share != 1:
		# 			frappe.throw(_("Sorry! User should have complete access to their own record."))
		# 	else:
		# 		frappe.throw(_("Sorry! Sharing with Website User is prohibited."))

	def send_password_notification(self, new_password):
		try:
			if self.flags.in_insert:
				if self.name not in STANDARD_USERS:
					if new_password:
						# new password given, no email required
						_update_password(
							user=self.name, pwd=new_password, logout_all_sessions=self.logout_all_sessions
						)

					if (
						not self.flags.no_welcome_mail
						and cint(self.send_welcome_email)
						and not self.flags.email_sent
					):
						self.send_welcome_mail_to_user()
						self.flags.email_sent = 1
						if frappe.session.user != "Guest":
							msgprint(_("Welcome email sent"))
						return
			else:
				self.email_new_password(new_password)

		except frappe.OutgoingEmailError:
			frappe.clear_last_message()
			frappe.msgprint(
				_("Please setup default outgoing Email Account from Settings > Email Account"), alert=True
			)
			# email server not set, don't send email
			self.log_error("Unable to send new password notification")

	@Document.hook
	def validate_reset_password(self):
		pass

	def reset_password(self, send_email=False, password_expired=False):
		from frappe.utils import get_url

		key = frappe.generate_hash()
		hashed_key = sha256_hash(key)
		self.db_set("reset_password_key", hashed_key)
		self.db_set("last_reset_password_key_generated_on", now_datetime())

		url = "/update-password?key=" + key
		if password_expired:
			url = "/update-password?key=" + key + "&password_expired=true"

		link = get_url(url)
		if send_email:
			self.password_reset_mail(link)

		return link

	def get_fullname(self):
		"""get first_name space last_name"""
		return (self.first_name or "") + (self.first_name and " " or "") + (self.last_name or "")

	def password_reset_mail(self, link):
		reset_password_template = frappe.db.get_system_setting("reset_password_template")

		self.send_login_mail(
			_("Password Reset"),
			"password_reset",
			{"link": link},
			now=True,
			custom_template=reset_password_template,
		)

	def send_welcome_mail_to_user(self):
		from frappe.utils import get_url

		link = self.reset_password()
		subject = None
		method = frappe.get_hooks("welcome_email")
		if method:
			subject = frappe.get_attr(method[-1])()
		if not subject:
			site_name = frappe.db.get_default("site_name") or frappe.get_conf().get("site_name")
			if site_name:
				subject = _("Welcome to {0}").format(site_name)
			else:
				subject = _("Complete Registration")

		welcome_email_template = frappe.db.get_system_setting("welcome_email_template")

		self.send_login_mail(
			subject,
			"new_user",
			dict(
				link=link,
				site_url=get_url(),
			),
			custom_template=welcome_email_template,
		)

	def send_login_mail(self, subject, template, add_args, now=None, custom_template=None):
		"""send mail with login details"""
		from frappe.utils import get_url
		from frappe.utils.user import get_user_fullname

		created_by = get_user_fullname(frappe.session["user"])
		if created_by == "Guest":
			created_by = "Administrator"

		args = {
			"first_name": self.first_name or self.last_name or "user",
			"user": self.name,
			"title": subject,
			"login_url": get_url(),
			"created_by": created_by,
		}

		args.update(add_args)

		sender = (
			frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user) or None
		)

		if custom_template:
			from frappe.email.doctype.email_template.email_template import get_email_template

			email_template = get_email_template(custom_template, args)
			subject = email_template.get("subject")
			content = email_template.get("message")

		frappe.sendmail(
			recipients=self.email,
			sender=sender,
			subject=subject,
			template=template if not custom_template else None,
			content=content if custom_template else None,
			args=args,
			header=[subject, "green"],
			delayed=(not now) if now is not None else self.flags.delay_emails,
			retry=3,
		)

	def on_trash(self):
		frappe.clear_cache(user=self.name)
		if self.name in STANDARD_USERS:
			throw(_("User {0} cannot be deleted").format(self.name))

		# disable the user and log him/her out
		self.enabled = 0
		if getattr(frappe.local, "login_manager", None):
			frappe.local.login_manager.logout(user=self.name)

		# delete todos
		frappe.db.delete("ToDo", {"allocated_to": self.name})
		todo_table = DocType("ToDo")
		(
			frappe.qb.update(todo_table)
			.set(todo_table.assigned_by, None)
			.where(todo_table.assigned_by == self.name)
		).run()

		# delete events
		frappe.db.delete("Event", {"owner": self.name, "event_type": "Private"})

		# delete shares
		frappe.db.delete("DocShare", {"user": self.name})
		# delete messages
		table = DocType("Communication")
		frappe.db.delete(
			table,
			filters=(
				(table.communication_type.isin(["Chat", "Notification"]))
				& (table.reference_doctype == "User")
				& ((table.reference_name == self.name) | table.owner == self.name)
			),
			run=False,
		)
		# unlink contact
		table = DocType("Contact")
		frappe.qb.update(table).where(table.user == self.name).set(table.user, None).run()

		# delete notification settings
		frappe.delete_doc("Notification Settings", self.name, ignore_permissions=True)

		if self.get("allow_in_mentions"):
			frappe.cache.delete_key("users_for_mentions")

		frappe.cache.delete_key("enabled_users")

		# delete user permissions
		frappe.db.delete("User Permission", {"user": self.name})

		# Delete OAuth data
		frappe.db.delete("OAuth Authorization Code", {"user": self.name})
		frappe.db.delete("Token Cache", {"user": self.name})

		# Delete EPS data
		frappe.db.delete("Energy Point Log", {"user": self.name})

		# Remove user link from Workflow Action
		frappe.db.set_value("Workflow Action", {"user": self.name}, "user", None)

		# Delete user's List Filters
		frappe.db.delete("List Filter", {"for_user": self.name})

		# Remove user from Note's Seen By table
		seen_notes = frappe.get_all("Note", filters=[["Note Seen By", "user", "=", self.name]], pluck="name")
		for note_id in seen_notes:
			note = frappe.get_doc("Note", note_id)
			for row in note.seen_by:
				if row.user == self.name:
					note.remove(row)
			note.save(ignore_permissions=True)

	def before_rename(self, old_name, new_name, merge=False):
		# if merging, delete the old user notification settings
		if merge:
			frappe.delete_doc("Notification Settings", old_name, ignore_permissions=True)

		frappe.clear_cache(user=old_name)
		self.validate_rename(old_name, new_name)

	def validate_rename(self, old_name, new_name):
		# do not allow renaming administrator and guest
		if old_name in STANDARD_USERS:
			throw(_("User {0} cannot be renamed").format(self.name))

		self.validate_email_type(new_name)

	def validate_email_type(self, email):
		from frappe.utils import validate_email_address

		validate_email_address(email.strip(), True)

	def after_rename(self, old_name, new_name, merge=False):
		tables = frappe.db.get_tables()
		for tab in tables:
			desc = frappe.db.get_table_columns_description(tab)
			has_fields = [d.get("name") for d in desc if d.get("name") in ["owner", "modified_by"]]
			for field in has_fields:
				frappe.db.sql(
					"""UPDATE `{}`
					SET `{}` = {}
					WHERE `{}` = {}""".format(tab, field, "%s", field, "%s"),
					(new_name, old_name),
				)

		if frappe.db.exists("Notification Settings", old_name):
			frappe.rename_doc("Notification Settings", old_name, new_name, force=True, show_alert=False)

		# set email
		frappe.db.set_value("User", new_name, "email", new_name)

	def append_roles(self, *roles):
		"""Add roles to user"""
		current_roles = {d.role for d in self.get("roles")}
		for role in roles:
			if role in current_roles:
				continue
			self.append("roles", {"role": role})

	def add_roles(self, *roles):
		"""Add roles to user and save"""
		self.append_roles(*roles)
		self.save()

	def remove_roles(self, *roles):
		existing_roles = {d.role: d for d in self.get("roles")}
		for role in roles:
			if role in existing_roles:
				self.get("roles").remove(existing_roles[role])

		self.save()

	def remove_all_roles_for_guest(self):
		if self.name == "Guest":
			self.set("roles", list({d for d in self.get("roles") if d.role == "Guest"}))

	def remove_disabled_roles(self):
		disabled_roles = [d.name for d in frappe.get_all("Role", filters={"disabled": 1})]
		for role in list(self.get("roles")):
			if role.role in disabled_roles:
				self.get("roles").remove(role)

	def ensure_unique_roles(self):
		exists = set()
		for d in list(self.roles):
			if (not d.role) or (d.role in exists):
				self.roles.remove(d)
			exists.add(d.role)

	def ensure_unique_role_profiles(self):
		seen = set()
		for rp in list(self.role_profiles):
			if rp.role_profile in seen:
				self.role_profiles.remove(rp)
			seen.add(rp.role_profile)

	def validate_username(self):
		if not self.username and self.is_new() and self.first_name:
			self.username = frappe.scrub(self.first_name)

		if not self.username:
			return

		# strip space and @
		self.username = self.username.strip(" @")

		if self.username_exists():
			if self.user_type == "System User":
				frappe.msgprint(_("Username {0} already exists").format(self.username))
				self.suggest_username()

			self.username = ""

	def password_strength_test(self):
		"""test password strength"""
		if self.flags.ignore_password_policy:
			return

		if self.__new_password:
			user_data = (self.first_name, self.middle_name, self.last_name, self.email, self.birth_date)
			result = test_password_strength(self.__new_password, user_data=user_data)
			feedback = result.get("feedback", None)

			if feedback and not feedback.get("password_policy_validation_passed", False):
				handle_password_test_fail(feedback)

	def suggest_username(self):
		def _check_suggestion(suggestion):
			if self.username != suggestion and not self.username_exists(suggestion):
				return suggestion

			return None

		# @firstname
		username = _check_suggestion(frappe.scrub(self.first_name))

		if not username:
			# @firstname_last_name
			username = _check_suggestion(frappe.scrub("{} {}".format(self.first_name, self.last_name or "")))

		if username:
			frappe.msgprint(_("Suggested Username: {0}").format(username))

		return username

	def username_exists(self, username=None):
		return frappe.db.get_value("User", {"username": username or self.username, "name": ("!=", self.name)})

	def get_blocked_modules(self):
		"""Return list of modules blocked for that user."""
		return [d.module for d in self.block_modules] if self.block_modules else []

	def validate_user_email_inbox(self):
		"""check if same email account added in User Emails twice"""

		email_accounts = [user_email.email_account for user_email in self.user_emails]
		if len(email_accounts) != len(set(email_accounts)):
			frappe.throw(_("Email Account added multiple times"))

	def get_social_login_userid(self, provider: str):
		try:
			for p in self.social_logins:
				if p.provider == provider:
					return p.userid
		except Exception:
			return None

	def set_social_login_userid(self, provider, userid, username=None):
		social_logins = {"provider": provider, "userid": userid}

		if username:
			social_logins["username"] = username

		self.append("social_logins", social_logins)

	def get_restricted_ip_list(self):
		return get_restricted_ip_list(self)

	@classmethod
	def find_by_credentials(cls, user_name: str, password: str, validate_password: bool = True):
		"""Find the user by credentials.

		This is a login utility that needs to check login related system settings while finding the user.
		1. Find user by email ID by default
		2. If allow_login_using_mobile_number is set, you can use mobile number while finding the user.
		3. If allow_login_using_user_name is set, you can use username while finding the user.
		"""

		login_with_mobile = cint(frappe.get_system_settings("allow_login_using_mobile_number"))
		login_with_username = cint(frappe.get_system_settings("allow_login_using_user_name"))

		or_filters = [{"name": user_name}]
		if login_with_mobile:
			or_filters.append({"mobile_no": user_name})
		if login_with_username:
			or_filters.append({"username": user_name})

		users = frappe.get_all("User", fields=["name", "enabled"], or_filters=or_filters, limit=1)
		if not users:
			return

		user = users[0]
		user["is_authenticated"] = True
		if validate_password:
			try:
				check_password(user["name"], password, delete_tracker_cache=False)
			except frappe.AuthenticationError:
				user["is_authenticated"] = False

		return user

	def set_time_zone(self):
		if not self.time_zone:
			self.time_zone = get_system_timezone()

	def get_permission_log_options(self, event=None):
		return {"fields": ("role_profile_name", "roles", "module_profile", "block_modules")}

	def check_roles_added(self):
		if self.user_type != "System User" or self.roles or not self.is_new():
			return

		frappe.msgprint(
			_("Newly created user {0} has no roles enabled.").format(frappe.bold(self.name)),
			title=_("No Roles Specified"),
			indicator="orange",
			primary_action={
				"label": _("Add Roles"),
				"client_action": "frappe.set_route",
				"args": ["Form", self.doctype, self.name],
			},
		)


@frappe.whitelist()
def get_timezones():
	import pytz

	return {"timezones": pytz.all_timezones}


@frappe.whitelist()
def get_all_roles():
	"""return all roles"""
	active_domains = frappe.get_active_domains()

	roles = frappe.get_all(
		"Role",
		filters={
			"name": ("not in", frappe.permissions.AUTOMATIC_ROLES),
			"disabled": 0,
		},
		or_filters={"ifnull(restrict_to_domain, '')": "", "restrict_to_domain": ("in", active_domains)},
		order_by="name",
	)

	return sorted([role.get("name") for role in roles])


@frappe.whitelist()
def get_roles(arg=None):
	"""get roles for a user"""
	return frappe.get_roles(frappe.form_dict["uid"])


@frappe.whitelist()
def get_perm_info(role):
	"""get permission info"""
	from frappe.permissions import get_all_perms

	return get_all_perms(role)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_password(
	new_password: str, logout_all_sessions: int = 0, key: str | None = None, old_password: str | None = None
):
	"""Update password for the current user.

	Args:
	    new_password (str): New password.
	    logout_all_sessions (int, optional): If set to 1, all other sessions will be logged out. Defaults to 0.
	    key (str, optional): Password reset key. Defaults to None.
	    old_password (str, optional): Old password. Defaults to None.
	"""

	if len(new_password) > MAX_PASSWORD_SIZE:
		frappe.throw(_("Password size exceeded the maximum allowed size."))

	result = test_password_strength(new_password)
	feedback = result.get("feedback", None)

	if feedback and not feedback.get("password_policy_validation_passed", False):
		handle_password_test_fail(feedback)

	res = _get_user_for_update_password(key, old_password)
	if res.get("message"):
		frappe.local.response.http_status_code = 410
		return res["message"]
	else:
		user = res["user"]

	logout_all_sessions = cint(logout_all_sessions) or frappe.get_system_settings("logout_on_password_reset")
	_update_password(user, new_password, logout_all_sessions=cint(logout_all_sessions))

	user_doc, redirect_url = reset_user_data(user)

	# get redirect url from cache
	redirect_to = frappe.cache.hget("redirect_after_login", user)
	if redirect_to:
		redirect_url = redirect_to
		frappe.cache.hdel("redirect_after_login", user)

	frappe.local.login_manager.login_as(user)

	frappe.db.set_value("User", user, "last_password_reset_date", today())
	frappe.db.set_value("User", user, "reset_password_key", "")

	if user_doc.user_type == "System User":
		return get_default_path() or "/app"
	else:
		return redirect_url or get_default_path() or get_home_page()


@frappe.whitelist(allow_guest=True)
def test_password_strength(new_password: str, key=None, old_password=None, user_data: tuple | None = None):
	from frappe.utils.password_strength import test_password_strength as _test_password_strength

	if key is not None or old_password is not None:
		from frappe.deprecation_dumpster import deprecation_warning

		deprecation_warning(
			"unknown",
			"v17",
			"Arguments `key` and `old_password` are deprecated in function `test_password_strength`.",
		)

	enable_password_policy = frappe.get_system_settings("enable_password_policy")

	if not enable_password_policy:
		return {}

	if not user_data:
		user_data = frappe.db.get_value(
			"User", frappe.session.user, ["first_name", "middle_name", "last_name", "email", "birth_date"]
		)

	if new_password:
		result = _test_password_strength(new_password, user_inputs=user_data)
		password_policy_validation_passed = False
		minimum_password_score = cint(frappe.get_system_settings("minimum_password_score"))

		# score should be greater than 0 and minimum_password_score
		if result.get("score") and result.get("score") >= minimum_password_score:
			password_policy_validation_passed = True

		result["feedback"]["password_policy_validation_passed"] = password_policy_validation_passed
		result.pop("password", None)
		return result


@frappe.whitelist()
def has_email_account(email: str):
	return frappe.get_list("Email Account", filters={"email_id": email})


@frappe.whitelist(allow_guest=False)
def get_email_awaiting(user):
	return frappe.get_all(
		"User Email",
		fields=["email_account", "email_id"],
		filters={"awaiting_password": 1, "parent": user, "used_oauth": 0},
	)


def ask_pass_update():
	# update the sys defaults as to awaiting users
	from frappe.utils import set_default

	password_list = frappe.get_all(
		"User Email", filters={"awaiting_password": 1, "used_oauth": 0}, pluck="parent", distinct=True
	)
	set_default("email_user_password", ",".join(password_list))


def _get_user_for_update_password(key, old_password):
	# verify old password
	result = frappe._dict()
	if key:
		hashed_key = sha256_hash(key)
		user = frappe.db.get_value(
			"User", {"reset_password_key": hashed_key}, ["name", "last_reset_password_key_generated_on"]
		)
		result.user, last_reset_password_key_generated_on = user or (None, None)
		if result.user:
			reset_password_link_expiry = cint(
				frappe.get_system_settings("reset_password_link_expiry_duration")
			)
			if (
				reset_password_link_expiry
				and now_datetime()
				> last_reset_password_key_generated_on + timedelta(seconds=reset_password_link_expiry)
			):
				result.message = _("The reset password link has been expired")
		else:
			result.message = _("The reset password link has either been used before or is invalid")
	elif old_password:
		# verify old password
		frappe.local.login_manager.check_password(frappe.session.user, old_password)
		user = frappe.session.user
		result.user = user
	return result


def reset_user_data(user):
	user_doc = frappe.get_doc("User", user)
	redirect_url = user_doc.redirect_url
	user_doc.reset_password_key = ""
	user_doc.redirect_url = ""
	user_doc.save(ignore_permissions=True)

	return user_doc, redirect_url


@frappe.whitelist(methods=["POST"])
def verify_password(password):
	frappe.local.login_manager.check_password(frappe.session.user, password)


@frappe.whitelist(allow_guest=True)
def sign_up(email: str, first_name: str, last_name: str, redirect_to: str, university: str = None, major: str = None) -> tuple[int, str]:
    if is_signup_disabled():
        frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))

    user = frappe.db.get("User", {"email": email})
    if user:
        if user.enabled:
            return 0, _("Already Registered")
        else:
            return 0, _("Registered but disabled")
    else:
        if frappe.db.get_creation_count("User", 60) > 300:
            frappe.respond_as_web_page(
                _("Temporarily Disabled"),
                _("Too many users signed up recently, so the registration is disabled. Please try back in an hour"),
                http_status_code=429,
            )

        from frappe.utils import random_string

        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": escape_html(first_name),
            "last_name": escape_html(last_name),
            "enabled": 1,
            "university": university,
            "major": major,
            "new_password": random_string(10),
            "user_type": "Website User",
            "send_welcome_email": 1
        })
        
        # Prevent modification timestamp conflicts
        user.flags.ignore_permissions = True
        user.flags.ignore_password_policy = True
        user.flags.ignore_timestamps = True
        user.flags.in_insert = True
        
        # Insert the user
        user.insert(ignore_permissions=True)

        # Set any additional fields without triggering timestamp updates
        if university:
            frappe.db.set_value("User", user.name, "university", university, update_modified=False)
        if major:
            frappe.db.set_value("User", user.name, "major", major, update_modified=False)

        # set default signup role as per Portal Settings
        default_role = frappe.db.get_single_value("Portal Settings", "default_role")
        if default_role:
            user.add_roles(default_role)

        # Handle redirect
        if redirect_to:
            frappe.cache.hset("redirect_after_login", user.name, redirect_to)

        # Send welcome email
        try:
            user.send_welcome_mail_to_user()
            return 1, _("Please check your email for verification")
        except Exception as e:
            frappe.log_error(f"Failed to send welcome email to {email}: {str(e)}")
            return 1, _("Please check your email for verification")  # Still return success

@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=get_password_reset_limit, seconds=60 * 60)
def reset_password(user: str) -> str:
	try:
		user: User = frappe.get_doc("User", user)
		if user.name == "Administrator":
			return "not allowed"
		if not user.enabled:
			return "disabled"

		user.validate_reset_password()
		user.reset_password(send_email=True)

		return frappe.msgprint(
			msg=_("Password reset instructions have been sent to {}'s email").format(user.full_name),
			title=_("Password Email Sent"),
		)
	except frappe.DoesNotExistError:
		frappe.local.response["http_status_code"] = 404
		frappe.clear_messages()
		return "not found"


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def user_query(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import get_filters_cond, get_match_cond

	doctype = "User"
	conditions = []

	user_type_condition = "and user_type != 'Website User'"
	if filters and filters.get("ignore_user_type") and frappe.session.data.user_type == "System User":
		user_type_condition = ""
	filters and filters.pop("ignore_user_type", None)

	txt = f"%{txt}%"
	return frappe.db.sql(
		"""SELECT `name`, CONCAT_WS(' ', first_name, middle_name, last_name)
        FROM `tabUser`
        WHERE `enabled`=1
            {user_type_condition}
            AND `docstatus` < 2
            AND `name` NOT IN ({standard_users})
            AND ({key} LIKE %(txt)s
                OR CONCAT_WS(' ', first_name, middle_name, last_name) LIKE %(txt)s)
            {fcond} {mcond}
        ORDER BY
            CASE WHEN `name` LIKE %(txt)s THEN 0 ELSE 1 END,
            CASE WHEN concat_ws(' ', first_name, middle_name, last_name) LIKE %(txt)s
                THEN 0 ELSE 1 END,
            NAME asc
        LIMIT %(page_len)s OFFSET %(start)s
    """.format(
			user_type_condition=user_type_condition,
			standard_users=", ".join(frappe.db.escape(u) for u in STANDARD_USERS),
			key=searchfield,
			fcond=get_filters_cond(doctype, filters, conditions),
			mcond=get_match_cond(doctype),
		),
		dict(start=start, page_len=page_len, txt=txt),
	)


def get_total_users():
	"""Return total number of system users."""
	return flt(
		frappe.db.sql(
			"""SELECT SUM(`simultaneous_sessions`)
		FROM `tabUser`
		WHERE `enabled` = 1
		AND `user_type` = 'System User'
		AND `name` NOT IN ({})""".format(", ".join(["%s"] * len(STANDARD_USERS))),
			STANDARD_USERS,
		)[0][0]
	)


def get_system_users(exclude_users: Iterable[str] | str | None = None, limit: int | None = None):
	_excluded_users = list(STANDARD_USERS)
	if isinstance(exclude_users, str):
		_excluded_users.append(exclude_users)
	elif isinstance(exclude_users, Iterable):
		_excluded_users.extend(exclude_users)

	return frappe.get_all(
		"User",
		filters={
			"enabled": 1,
			"user_type": ("!=", "Website User"),
			"name": ("not in", _excluded_users),
		},
		pluck="name",
		limit=limit,
	)


def get_active_users():
	"""Return number of system users who logged in, in the last 3 days."""
	return frappe.db.sql(
		"""select count(*) from `tabUser`
		where enabled = 1 and user_type != 'Website User'
		and name not in ({})
		and hour(timediff(now(), last_active)) < 72""".format(", ".join(["%s"] * len(STANDARD_USERS))),
		STANDARD_USERS,
	)[0][0]


def get_website_users():
	"""Return total number of website users."""
	return frappe.db.count("User", filters={"enabled": True, "user_type": "Website User"})


def get_active_website_users():
	"""Return number of website users who logged in, in the last 3 days."""
	return frappe.db.sql(
		"""select count(*) from `tabUser`
        where enabled = 1 and user_type = 'Website User'
        and hour(timediff(now(), last_active)) < 72"""
	)[0][0]


def get_permission_query_conditions(user):
	if user == "Administrator":
		return ""
	else:
		return """(`tabUser`.name not in ({standard_users}))""".format(
			standard_users=", ".join(frappe.db.escape(user) for user in STANDARD_USERS)
		)


def has_permission(doc, user):
	if (user != "Administrator") and (doc.name in STANDARD_USERS):
		# dont allow non Administrator user to view / edit Administrator user
		return False
	return True


def notify_admin_access_to_system_manager(login_manager=None):
	if (
		login_manager
		and login_manager.user == "Administrator"
		and frappe.local.conf.notify_admin_access_to_system_manager
	):
		site = '<a href="{0}" target="_blank">{0}</a>'.format(frappe.local.request.host_url)
		date_and_time = "<b>{}</b>".format(format_datetime(now_datetime(), format_string="medium"))
		ip_address = frappe.local.request_ip

		access_message = _("Administrator accessed {0} on {1} via IP Address {2}.").format(
			site, date_and_time, ip_address
		)

		frappe.sendmail(
			recipients=get_system_managers(),
			subject=_("Administrator Logged In"),
			template="administrator_logged_in",
			args={"access_message": access_message},
			header=["Access Notification", "orange"],
		)


def handle_password_test_fail(feedback: dict):
	# Backward compatibility
	if "feedback" in feedback:
		feedback = feedback["feedback"]

	suggestions = feedback.get("suggestions", [])
	warning = feedback.get("warning", "")

	frappe.throw(msg=" ".join([warning, *suggestions]), title=_("Invalid Password"))


def update_gravatar(name):
	gravatar = has_gravatar(name)
	if gravatar:
		frappe.db.set_value("User", name, "user_image", gravatar)


def throttle_user_creation():
	if frappe.flags.in_import:
		return

	if frappe.db.get_creation_count("User", 60) > frappe.local.conf.get("throttle_user_limit", 60):
		frappe.throw(_("Throttled"))


@frappe.whitelist()
def get_module_profile(module_profile: str):
	module_profile = frappe.get_doc("Module Profile", {"module_profile_name": module_profile})
	return module_profile.get("block_modules")


def create_contact(user, ignore_links=False, ignore_mandatory=False):
	from frappe.contacts.doctype.contact.contact import get_contact_name

	if user.name in ["Administrator", "Guest"]:
		return

	contact_name = get_contact_name(user.email)
	if not contact_name:
		try:
			contact = frappe.get_doc(
				{
					"doctype": "Contact",
					"first_name": user.first_name,
					"last_name": user.last_name,
					"user": user.name,
					"gender": user.gender,
				}
			)

			if user.email:
				contact.add_email(user.email, is_primary=True)

			if user.phone:
				contact.add_phone(user.phone, is_primary_phone=True)

			if user.mobile_no:
				contact.add_phone(user.mobile_no, is_primary_mobile_no=True)

			contact.insert(
				ignore_permissions=True, ignore_links=ignore_links, ignore_mandatory=ignore_mandatory
			)
		except frappe.DuplicateEntryError:
			pass
	else:
		try:
			contact = frappe.get_doc("Contact", contact_name)
			contact.first_name = user.first_name
			contact.last_name = user.last_name
			contact.gender = user.gender

			# Add mobile number if phone does not exists in contact
			if user.phone and not any(new_contact.phone == user.phone for new_contact in contact.phone_nos):
				# Set primary phone if there is no primary phone number
				contact.add_phone(
					user.phone,
					is_primary_phone=not any(
						new_contact.is_primary_phone == 1 for new_contact in contact.phone_nos
					),
				)

			# Add mobile number if mobile does not exists in contact
			if user.mobile_no and not any(
				new_contact.phone == user.mobile_no for new_contact in contact.phone_nos
			):
				# Set primary mobile if there is no primary mobile number
				contact.add_phone(
					user.mobile_no,
					is_primary_mobile_no=not any(
						new_contact.is_primary_mobile_no == 1 for new_contact in contact.phone_nos
					),
				)

			contact.save(ignore_permissions=True)
		except frappe.TimestampMismatchError:
			raise frappe.RetryBackgroundJobError


def get_restricted_ip_list(user):
	if not user.restrict_ip:
		return

	return [i.strip() for i in user.restrict_ip.split(",")]


@frappe.whitelist(methods=["POST"])
def generate_keys(user: str):
	"""
	generate api key and api secret

	:param user: str
	"""
	frappe.only_for("System Manager")
	user_details: User = frappe.get_doc("User", user)
	api_secret = frappe.generate_hash(length=15)
	# if api key is not set generate api key
	if not user_details.api_key:
		api_key = frappe.generate_hash(length=15)
		user_details.api_key = api_key
	user_details.api_secret = api_secret
	user_details.save()

	return {"api_secret": api_secret}


@frappe.whitelist()
def switch_theme(theme):
	if theme in ["Dark", "Light", "Automatic"]:
		frappe.db.set_value("User", frappe.session.user, "desk_theme", theme)


def get_enabled_users():
	def _get_enabled_users():
		enabled_users = frappe.get_all("User", filters={"enabled": "1"}, pluck="name")
		return enabled_users

	return frappe.cache.get_value("enabled_users", _get_enabled_users)


@frappe.whitelist(methods=["POST"])
def impersonate(user: str, reason: str):
	# Note: For now we only allow admins, we MIGHT allow system manager in future.
	# All the impersonation code doesn't assume anything about user.
	frappe.only_for("Administrator")

	impersonator = frappe.session.user
	frappe.get_doc(
		{
			"doctype": "Activity Log",
			"user": user,
			"status": "Success",
			"subject": _("User {0} impersonated as {1}").format(impersonator, user),
			"operation": "Impersonate",
		}
	).insert(ignore_permissions=True, ignore_links=True)

	notification = frappe.new_doc(
		"Notification Log",
		for_user=user,
		from_user=frappe.session.user,
		subject=_("{0} just impersonated as you. They gave this reason: {1}").format(impersonator, reason),
	)
	notification.set("type", "Alert")
	notification.insert(ignore_permissions=True)
	frappe.local.login_manager.impersonate(user)
